# 🚀 Premium Developer Portfolio Website

Welcome to your new personal portfolio website! This project is a premium, modern, and highly interactive single-page portfolio designed using Vanilla HTML5, CSS3 (with custom design system variables, glassmorphic UI, HSL theme maps), and JavaScript. It features an automated typing banner, scroll-triggered experience meters, career milestone timelines, and contact verification.

## 🔗 Live Site URL
Once deployed, your portfolio will be visible at:
**[https://harsha-karimikonda.github.io/](https://harsha-karimikonda.github.io/)**

---

## 🎨 Features
- **Modern Theme Toggle**: Fully integrated dark and light themes with state persistence using browser `localStorage`.
- **Dynamic Backgrounds**: CSS-based mesh glowing blur vectors that drift behind elements.
- **Glassmorphism**: Backdrop blur overlays with responsive border glows.
- **Animated Skill Meters**: Circular/horizontal bars that animate dynamically as you scroll them into view.
- **Project Grid Filters**: Instant client-side tag filtering for projects (Frontend vs Backend).
- **Responsive Navigation**: Glassmorphic, sticky top navbar with a mobile hamburger overlay menu.
- **Form Verification**: Intercepted submit handlers with beautiful load spinners and success animations.

---

## 🚀 How to Host on GitHub Pages (Internet)

To serve this website on your root domain (`https://harsha-karimikonda.github.io/`), follow these quick steps:

### Step 1: Rename your repository on GitHub
1. Go to your repository settings page: [https://github.com/Harsha-Karimikonda/portfolio.github.io/settings](https://github.com/Harsha-Karimikonda/portfolio.github.io/settings).
2. In the **Repository Name** text input box, rename it from `portfolio.github.io` to:
   **`harsha-karimikonda.github.io`**
3. Click the **Rename** button.

### Step 2: Update local Git remote and push the files
Open your terminal (PowerShell / Command Prompt) in the directory of this project (`d:\portfolio.github.io`) and execute:

```bash
# Update the Git origin url to point to the renamed repository
git remote set-url origin https://github.com/Harsha-Karimikonda/harsha-karimikonda.github.io.git

# Stage all files
git add .

# Commit changes
git commit -m "feat: design and implement premium portfolio site"

# Push changes to GitHub
git push -u origin main
```

### Step 3: Enable Pages (if not automatically activated)
GitHub typically deploys root username repositories automatically. To check status:
1. Go to settings under `https://github.com/Harsha-Karimikonda/harsha-karimikonda.github.io/settings`.
2. Click **Pages** in the left sidebar.
3. Under **Build and deployment**, ensure the **Source** is set to **Deploy from a branch**.
4. Choose the **`main`** branch and the **`/ (root)`** directory, then click **Save**.
5. Wait 1–2 minutes, and check `https://harsha-karimikonda.github.io/`.

---

## 🛠️ Customizing Your Content
To customize the content of your site:
- **Profile details / Projects / Resume links**: Open `index.html` and search for standard HTML elements to change names, project descriptions, skills percentage values (`data-percentage="..."`), and email parameters.
- **Visuals & Accent Colors**: Modify the CSS custom properties inside `web.css` (e.g. `--accent-indigo`, `--accent-cyan`) to change the primary glow colors of the site.
