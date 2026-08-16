import type { Metadata } from "next";
import {
  Geist,
  Geist_Mono,
} from "next/font/google";

import { AppNav } from "@/components/AppNav";

import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  metadataBase: new URL(
    "https://laborlens-eosin.vercel.app",
  ),
  title: {
    default:
      "LaborLens — Point-in-Time Labor-Market Intelligence",
    template: "%s | LaborLens",
  },
  description:
    "Revision-aware labor-market research using FRED/ALFRED vintages, point-in-time reconstruction, release-aware replay, evidence validation, and grounded AI explanations.",
};

export default function RootLayout({
  children,
}: LayoutProps<"/">) {
  const mode =
    process.env.NEXT_PUBLIC_LABORLENS_MODE ??
    "demo";

  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body>
        <div className="desktop-stage">
          <div className="app-window">
            <div className="window-titlebar">
              <div className="flex items-center gap-3">
                <span className="window-icon" />

                <span className="window-title">
                  LaborLens Research Workstation
                </span>
              </div>

              <div className="window-controls">
                <span className="window-control">
                  ─
                </span>

                <span className="window-control">
                  □
                </span>

                <span className="window-control">
                  ×
                </span>
              </div>
            </div>

            <AppNav mode={mode} />

            <div className="app-workspace">
              {children}
            </div>

            <footer className="window-statusbar">
              <div className="flex items-center gap-5">
                <span className="flex items-center gap-2">
                  <span className="status-light status-green" />
                  API ONLINE
                </span>

                <span>
                  MODE:{mode.toUpperCase()}
                </span>

                <span className="hidden sm:inline">
                  ENGINE:POINT-IN-TIME
                </span>
              </div>

              <div className="hidden md:block">
                FRED/ALFRED · REVISION-AWARE
              </div>
            </footer>
          </div>
        </div>
      </body>
    </html>
  );
}
