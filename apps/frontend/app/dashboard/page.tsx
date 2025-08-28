import Link from 'next/link'
import {
    Search,
    Database,
    TrendingUp,
    Users,
    Upload,
    BarChart3,
    ArrowUpRight,
    ArrowDownRight,
    Eye,
    ShoppingCart,
    Clock
} from 'lucide-react'

const stats = [
    { name: 'Total Products', value: '12,847', change: '+12%', changeType: 'positive', icon: Database },
    { name: 'Total Searches', value: '45,231', change: '+23%', changeType: 'positive', icon: Search },
    { name: 'Conversion Rate', value: '3.2%', change: '+0.8%', changeType: 'positive', icon: TrendingUp },
    { name: 'Active Users', value: '1,234', change: '+5%', changeType: 'positive', icon: Users },
]

const recentSearches = [
    { id: 1, query: 'red dress', results: 156, timestamp: '2 minutes ago', user: 'john@example.com' },
    { id: 2, query: 'blue jeans', results: 89, timestamp: '5 minutes ago', user: 'sarah@example.com' },
    { id: 3, query: 'white sneakers', results: 234, timestamp: '8 minutes ago', user: 'mike@example.com' },
    { id: 4, query: 'black handbag', results: 67, timestamp: '12 minutes ago', user: 'lisa@example.com' },
]

const quickActions = [
    { name: 'Upload Image', href: '/dashboard/search', icon: Upload, description: 'Search by image' },
    { name: 'View Catalog', href: '/dashboard/catalog', icon: Database, description: 'Manage products' },
    { name: 'Analytics', href: '/dashboard/reports', icon: BarChart3, description: 'View reports' },
    { name: 'Collections', href: '/dashboard/collections', icon: Eye, description: 'Browse collections' },
]

export default function Dashboard() {
    return (
        <div className="space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
                <p className="text-gray-600">Welcome back! Here's what's happening with your visual search.</p>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
                {stats.map((stat) => (
                    <div key={stat.name} className="bg-white overflow-hidden shadow rounded-lg">
                        <div className="p-5">
                            <div className="flex items-center">
                                <div className="flex-shrink-0">
                                    <stat.icon className="h-6 w-6 text-gray-400" />
                                </div>
                                <div className="ml-5 w-0 flex-1">
                                    <dl>
                                        <dt className="text-sm font-medium text-gray-500 truncate">{stat.name}</dt>
                                        <dd className="flex items-baseline">
                                            <div className="text-2xl font-semibold text-gray-900">{stat.value}</div>
                                            <div className={`ml-2 flex items-baseline text-sm font-semibold ${stat.changeType === 'positive' ? 'text-green-600' : 'text-red-600'
                                                }`}>
                                                {stat.changeType === 'positive' ? (
                                                    <ArrowUpRight className="self-center flex-shrink-0 h-4 w-4" />
                                                ) : (
                                                    <ArrowDownRight className="self-center flex-shrink-0 h-4 w-4" />
                                                )}
                                                <span className="sr-only">{stat.changeType === 'positive' ? 'Increased' : 'Decreased'} by</span>
                                                {stat.change}
                                            </div>
                                        </dd>
                                    </dl>
                                </div>
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            {/* Quick Actions */}
            <div>
                <h2 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h2>
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
                    {quickActions.map((action) => (
                        <Link
                            key={action.name}
                            href={action.href}
                            className="bg-white overflow-hidden shadow rounded-lg hover:shadow-md transition-shadow"
                        >
                            <div className="p-6">
                                <div className="flex items-center">
                                    <div className="flex-shrink-0">
                                        <action.icon className="h-8 w-8 text-blue-600" />
                                    </div>
                                    <div className="ml-4">
                                        <h3 className="text-sm font-medium text-gray-900">{action.name}</h3>
                                        <p className="text-sm text-gray-500">{action.description}</p>
                                    </div>
                                </div>
                            </div>
                        </Link>
                    ))}
                </div>
            </div>

            {/* Recent Activity */}
            <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
                {/* Recent Searches */}
                <div className="bg-white shadow rounded-lg">
                    <div className="px-4 py-5 sm:p-6">
                        <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Searches</h3>
                        <div className="flow-root">
                            <ul className="-my-5 divide-y divide-gray-200">
                                {recentSearches.map((search) => (
                                    <li key={search.id} className="py-4">
                                        <div className="flex items-center space-x-4">
                                            <div className="flex-shrink-0">
                                                <Search className="h-5 w-5 text-gray-400" />
                                            </div>
                                            <div className="flex-1 min-w-0">
                                                <p className="text-sm font-medium text-gray-900 truncate">
                                                    "{search.query}"
                                                </p>
                                                <p className="text-sm text-gray-500">
                                                    {search.results} results • {search.user}
                                                </p>
                                            </div>
                                            <div className="flex-shrink-0 text-sm text-gray-500">
                                                {search.timestamp}
                                            </div>
                                        </div>
                                    </li>
                                ))}
                            </ul>
                        </div>
                        <div className="mt-6">
                            <Link
                                href="/dashboard/search"
                                className="w-full flex justify-center items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
                            >
                                View all searches
                            </Link>
                        </div>
                    </div>
                </div>

                {/* System Status */}
                <div className="bg-white shadow rounded-lg">
                    <div className="px-4 py-5 sm:p-6">
                        <h3 className="text-lg font-medium text-gray-900 mb-4">System Status</h3>
                        <div className="space-y-4">
                            <div className="flex items-center justify-between">
                                <div className="flex items-center">
                                    <div className="w-2 h-2 bg-green-400 rounded-full mr-3"></div>
                                    <span className="text-sm text-gray-900">Search API</span>
                                </div>
                                <span className="text-sm text-gray-500">Operational</span>
                            </div>
                            <div className="flex items-center justify-between">
                                <div className="flex items-center">
                                    <div className="w-2 h-2 bg-green-400 rounded-full mr-3"></div>
                                    <span className="text-sm text-gray-900">Vector Database</span>
                                </div>
                                <span className="text-sm text-gray-500">Operational</span>
                            </div>
                            <div className="flex items-center justify-between">
                                <div className="flex items-center">
                                    <div className="w-2 h-2 bg-green-400 rounded-full mr-3"></div>
                                    <span className="text-sm text-gray-900">Image Processing</span>
                                </div>
                                <span className="text-sm text-gray-500">Operational</span>
                            </div>
                            <div className="flex items-center justify-between">
                                <div className="flex items-center">
                                    <div className="w-2 h-2 bg-yellow-400 rounded-full mr-3"></div>
                                    <span className="text-sm text-gray-900">Analytics</span>
                                </div>
                                <span className="text-sm text-gray-500">Degraded</span>
                            </div>
                        </div>
                        <div className="mt-6">
                            <Link
                                href="/dashboard/settings"
                                className="w-full flex justify-center items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
                            >
                                View system details
                            </Link>
                        </div>
                    </div>
                </div>
            </div>

            {/* Performance Metrics */}
            <div className="bg-white shadow rounded-lg">
                <div className="px-4 py-5 sm:p-6">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Performance Metrics</h3>
                    <div className="grid grid-cols-1 gap-5 sm:grid-cols-3">
                        <div className="text-center">
                            <div className="text-2xl font-bold text-blue-600">245ms</div>
                            <div className="text-sm text-gray-500">Average Search Time</div>
                        </div>
                        <div className="text-center">
                            <div className="text-2xl font-bold text-green-600">98.5%</div>
                            <div className="text-sm text-gray-500">Uptime</div>
                        </div>
                        <div className="text-center">
                            <div className="text-2xl font-bold text-purple-600">1,234</div>
                            <div className="text-sm text-gray-500">Searches Today</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}
