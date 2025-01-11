/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./sbily/tailwind.css",
    "./sbily/**/*.html",
    "./sbily/static/js/**/*.js",
  ],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      fontFamily: {
        inter: ["Inter", "sans-serif"],
      },
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      keyframes: {
        "toast-show": {
          from: { opacity: 0, transform: "translateY(-2rem)" },
          to: { opacity: 1, transform: "translateY(0)" },
        },
        "toast-hide": {
          from: { opacity: 1, transform: "translateX(0)" },
          to: { opacity: 0, transform: "translateX(2rem)" },
        },
        "dropdown-show": {
          to: { opacity: 1, transform: "translateY(0)" },
        },
        "dropdown-close": {
          from: { opacity: 1, transform: "translateY(0)" },
          to: { opacity: 0, transform: "translateY(0)" },
        },
        "dialog-show": {
          to: { opacity: 1 },
        },
        "dialog-close": {
          from: { opacity: 1 },
          to: { opacity: 0 },
        },
        "dialog-overlay-show": {
          to: { opacity: 1, "backdrop-filter": "blur(0.5rem)" },
        },
        "dialog-overlay-close": {
          from: { opacity: 1, "backdrop-filter": "blur(0.5rem)" },
          to: { opacity: 0, "backdrop-filter": "blur(0px)" },
        },
      },
      animation: {
        "toast-show": "toast-show 0.5s",
        "toast-hide": "toast-hide 0.5s forwards",
        "dropdown-show": "dropdown-show 0.5s forwards",
        "dropdown-close": "dropdown-close 0.5s forwards",
        "dialog-show": "dialog-show 0.5s forwards",
        "dialog-close": "dialog-close 0.5s forwards",
        "dialog-overlay-show": "dialog-overlay-show 0.5s forwards",
        "dialog-overlay-close": "dialog-overlay-close 0.5s forwards",
      },
    },
  },
  plugins: [],
};
