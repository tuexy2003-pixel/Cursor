import "./globals.css";
import type { ReactNode } from "react";

const links = [
  ["/", "Status"],
  ["/accounts", "Accounts"],
  ["/campaigns", "Campaigns"],
  ["/creatives", "Creatives"],
  ["/assets", "Assets"],
  ["/references", "References"],
  ["/experiments", "Experiments"],
  ["/posts", "Posts"],
  ["/comments", "Comments"],
  ["/benchmarks", "Benchmarks"],
  ["/policies", "Policies"],
  ["/runs", "Runs"],
  ["/company", "Company"],
];

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <nav>
          {links.map(([href, label]) => (
            <a key={href} href={href}>
              {label}
            </a>
          ))}
        </nav>
        <main>{children}</main>
      </body>
    </html>
  );
}
