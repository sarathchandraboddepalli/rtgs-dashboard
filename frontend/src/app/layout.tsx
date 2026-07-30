import type { Metadata } from 'next'
import './globals.css'
import Link from 'next/link'
export const metadata: Metadata = { title: 'AP RTGS Dashboard', description: 'Real-Time Governance Dashboard' }
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-gray-50 min-h-screen">
        <nav className="bg-blue-900 text-white px-6 py-4 flex items-center gap-8">
          <span className="font-bold text-lg">AP RTGS Dashboard</span>
          <Link href="/executive" className="hover:text-blue-200 text-sm">Executive</Link>
          <Link href="/schemes" className="hover:text-blue-200 text-sm">Schemes</Link>
          <Link href="/anomalies" className="hover:text-blue-200 text-sm">Anomalies</Link>
          <Link href="/query" className="hover:text-blue-200 text-sm">NL Query</Link>
        </nav>
        <main className="p-6">{children}</main>
      </body>
    </html>
  )
}
