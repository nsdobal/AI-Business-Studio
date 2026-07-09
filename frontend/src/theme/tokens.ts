export type ThemeMode = "light" | "dark";

export const themeTokens = {
  light: {
    background: "#f8fafc",
    surface: "#ffffff",
    surfaceMuted: "#f1f5f9",
    border: "#e2e8f0",
    text: "#0f172a",
    textMuted: "#64748b",
    primary: "#3567f5",
    primaryHover: "#2349e0",
  },
  dark: {
    background: "#0b1220",
    surface: "#111827",
    surfaceMuted: "#1e293b",
    border: "#334155",
    text: "#f8fafc",
    textMuted: "#94a3b8",
    primary: "#5a8fff",
    primaryHover: "#8eb6ff",
  },
} as const;
