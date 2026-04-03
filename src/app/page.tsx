import Link from 'next/link'

const artifacts = [
  {
    name: 'Rental Management',
    description:
      'AI assistant for landlords and property managers. Get help with lease terms, tenant communications, maintenance requests, and compliance questions.',
    href: '/rental-management',
  },
]

export default function Home() {
  return (
    <main className="min-h-screen py-16 px-4">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-4xl font-bold mb-2 text-gray-900">
          Claude Artifacts
        </h1>
        <p className="text-lg text-gray-600 mb-12">
          A portfolio of AI-powered tools built with Claude.
        </p>

        <div className="grid gap-6">
          {artifacts.map((artifact) => (
            <Link
              key={artifact.href}
              href={artifact.href}
              className="block p-6 bg-white rounded-xl border border-gray-200 shadow-sm hover:shadow-md hover:border-gray-300 transition-all duration-150"
            >
              <h2 className="text-xl font-semibold text-gray-900 mb-2">
                {artifact.name}
              </h2>
              <p className="text-gray-600 leading-relaxed">
                {artifact.description}
              </p>
              <span className="inline-block mt-4 text-sm font-medium text-indigo-600">
                Open artifact →
              </span>
            </Link>
          ))}
        </div>
      </div>
    </main>
  )
}
