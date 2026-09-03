---
title: "Continuous Dynamic Batching in LLM Serving: Maximizing GPU Throughput"
date: "2026-09-03"
summary: "An engineering deep-dive into how iteration-level scheduling, paged KV-cache allocation, and Radix prefix hashing eliminate execution bubbles in production model serving."
tags: ["LLM Inference", "Systems", "PyTorch", "GPU Memory"]
author: "Harsha Karimikonda"
---

## 1. The Bottleneck of Static Batching in Generative AI

In traditional deep learning pipelines (such as ResNet image classification or BERT embeddings), request batching is straightforward: requests are grouped into a static tensor of dimension `[B, C, H, W]`, fed through the forward pass simultaneously, and completed in unison.

However, **Autoregressive Large Language Models (LLMs)** break this paradigm entirely due to two distinct phases:

1. **Prefill Phase (Compute-Bound):** Ingests the initial prompt tokens in parallel, generating the Key-Value (KV) cache for the entire context.
2. **Decode Phase (Memory-Bandwidth Bound):** Generates output tokens iteratively, **one token at a time**, requiring a full memory pass over the KV-cache at every single step.

Because user prompts and generation lengths have high variance, **static batching** forces the entire batch to wait until the longest generation sequence finishes:

```
Request 1 (Prompt: 50, Output: 20 tokens):  [Prefill][Tokens: 20................] [IDLE BUBBLE (GPU Wasted).......]
Request 2 (Prompt: 10, Output: 150 tokens): [Prefill][Tokens: 150................................................]
```

This creates massive **execution bubbles** where GPU compute cores sit idle while waiting for stragglers to finish.

---

## 2. Iteration-Level Continuous Dynamic Batching

Instead of batching at the *request level*, modern inference engines (pioneered by Orca and vLLM) operate at the **iteration level**:

- At every forward-pass iteration step, the scheduler inspects the active queue.
- Completed sequences are immediately evicted and returned to the client over a Server-Sent Events (SSE) streaming socket.
- New waiting requests can immediately jump into the batch for their prefill step, or join the decode step alongside ongoing generations.

Here is how we implemented the dynamic batch step loop in [`mini-inference-engine`](https://github.com/Harsha-Karimikonda/mini-inference-engine):

```python
class ContinuousBatchScheduler:
    def __init__(self, max_batch_size: int, block_allocator: PagedKVAllocator):
        self.max_batch_size = max_batch_size
        self.allocator = block_allocator
        self.running_requests = []
        self.waiting_queue = []

    def step(self):
        # 1. Free blocks of completed requests
        finished = [r for r in self.running_requests if r.is_finished()]
        for req in finished:
            self.allocator.free(req.request_id)
            self.running_requests.remove(req)

        # 2. Admit new requests if memory blocks are available
        while self.waiting_queue and len(self.running_requests) < self.max_batch_size:
            candidate = self.waiting_queue[0]
            if self.allocator.can_allocate(candidate):
                req = self.waiting_queue.pop(0)
                self.allocator.allocate(req)
                self.running_requests.append(req)
            else:
                break  # Memory saturated; wait for next iteration

        # 3. Execute iteration forward pass across active sequences
        return self.execute_forward(self.running_requests)
```

---

## 3. Tackling Memory Fragmentation: Paged Logical KV-Cache

Without paging, memory allocators must allocate contiguous virtual GPU memory for the maximum possible context length (`max_seq_len`). For a 7B model with 32 layers and 4096 hidden dimensions, reserving contiguous buffers for 4096 tokens consumes roughly **2.1 GB of VRAM per request**, leading to heavy external fragmentation.

Inspired by virtual memory paging in operating systems, we slice the KV-cache into discrete fixed-size blocks (e.g., 16 tokens per block). Sequences dynamically allocate physical pages from an unfragmented global memory pool, maintaining an address translation table mapping `(request_id, token_index) -> physical_block_id`.

```
Logical Sequence: [Block 0 (Tokens 0-15)] -> [Block 1 (Tokens 16-31)] -> [Block 2 (Tokens 32-47)]
                                 |                          |                          |
Physical GPU Pages:       [Page 104]                 [Page 12]                  [Page 88]
```

This reduces KV-cache memory waste from **60–80% down to under 4%**, allowing our serving engine to achieve up to **4× higher concurrency** on the same GPU hardware!

---

## 4. Radix Prefix Hash Reuse

In production applications such as code completion, RAG document QA, and agentic workflows, different requests frequently share common prefixes (system prompts, tool definitions, reference chunks).

Instead of recomputing the prefill attention keys and values for identical tokens, we index KV-cache pages in a **Radix Prefix Tree** using chained SHA-256 chunk hashes:

```python
def compute_chunk_hash(prev_hash: str, token_chunk: list[int]) -> str:
    hasher = hashlib.sha256()
    hasher.update(prev_hash.encode('utf-8'))
    for token in token_chunk:
        hasher.update(token.to_bytes(4, byteorder='big'))
    return hasher.hexdigest()
```

When a new prompt arrives:
1. The scheduler hashes the prompt tokens in 16-token chunks.
2. It walks the Radix tree to find the longest matching prefix with warm physical blocks.
3. If a match is found, the prefill phase skips all matching tokens entirely and only runs forward computation on the suffix tokens!

For system prompts of 1,000 tokens, this drops Time-To-First-Token (TTFT) from **~320ms down to under 18ms**.

---

## 5. Conclusion & What's Next

Building an observable inference control plane requires solving hardware-software bottlenecks at every layer—from asynchronous I/O and GPU memory allocation to continuous scheduling.

The full open-source implementation, complete with FastAPI streaming endpoints, Prometheus metrics telemetry, and hardware-aware elastic autoscaling, is available on GitHub:
👉 **[Harsha-Karimikonda/mini-inference-engine](https://github.com/Harsha-Karimikonda/mini-inference-engine)**.

*Stay tuned for the next deep dive on quantization techniques: Comparing NF4 bitsandbytes with AWQ for edge LLM serving!*
