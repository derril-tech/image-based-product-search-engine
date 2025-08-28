'use client'

import { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
    Search,
    BarChart3,
    Settings,
    Users,
    Database,
    Upload,
    FolderOpen,
    LogOut,
    Menu,
    X,
    Bell,
    User
} from 'lucide-react'

const navigation = [
    { name: 'Overview', href: '/dashboard', icon: BarChart3 },
    { name: 'Search', href: '/dashboard/search', icon: Search },
    { name: 'Catalog', href: '/dashboard/catalog', icon: Database },
    { name: 'Collections', href: '/dashboard/collections', icon: FolderOpen },
    { name: 'Reports', href: '/dashboard/reports', icon: BarChart3 },
    { name: 'Team', href: '/dashboard/team', icon: Users },
    { name: 'Settings', href: '/dashboard/settings', icon: Settings },
]

export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode
}) {
    const [sidebarOpen, setSidebarOpen] = useState(false)
    const pathname = usePathname()

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Mobile sidebar */}
            <div className={`fixed inset-0 z-50 lg:hidden ${sidebarOpen ? 'block' : 'hidden'}`}>
                <div className="fixed inset-0 bg-gray-600 bg-opacity-75" onClick={() => setSidebarOpen(false)} />
                <div className="fixed inset-y-0 left-0 flex w-64 flex-col bg-white">
                    <div className="flex h-16 items-center justify-between px-4">
                        <div className="flex items-center">
                            <Search className="h-8 w-8 text-blue-600 mr-3" />
                            <span className="text-xl font-bold text-gray-900">VisualSearch</span>
                        </div>
                        <button
                            onClick={() => setSidebarOpen(false)}
                            className="text-gray-400 hover:text-gray-600"
                        >
                            <X className="h-6 w-6" />
                        </button>
                    </div>
                    <nav className="flex-1 space-y-1 px-2 py-4">
                        {navigation.map((item) => {
                            const isActive = pathname === item.href
                            return (
                                <Link
                                    key={item.name}
                                    href={item.href}
                                    className={`group flex items-center px-2 py-2 text-sm font-medium rounded-md transition-colors ${isActive
                                        ? 'bg-blue-100 text-blue-700'
                                        : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                                        }`}
                                    onClick={() => setSidebarOpen(false)}
                                >
                                    <item.icon className="mr-3 h-5 w-5" />
                                    {item.name}
                                </Link>
                            )
                        })}
                    </nav>
                </div>
            </div>

            {/* Desktop sidebar */}
            <div className="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-64 lg:flex-col">
                <div className="flex flex-col flex-grow bg-white border-r border-gray-200">
                    <div className="flex h-16 items-center px-4">
                        <Search className="h-8 w-8 text-blue-600 mr-3" />
                        <span className="text-xl font-bold text-gray-900">VisualSearch</span>
                    </div>
                    <nav className="flex-1 space-y-1 px-2 py-4">
                        {navigation.map((item) => {
                            const isActive = pathname === item.href
                            return (
                                <Link
                                    key={item.name}
                                    href={item.href}
                                    className={`group flex items-center px-2 py-2 text-sm font-medium rounded-md transition-colors ${isActive
                                        ? 'bg-blue-100 text-blue-700'
                                        : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                                        }`}
                                >
                                    <item.icon className="mr-3 h-5 w-5" />
                                    {item.name}
                                </Link>
                            )
                        })}
                    </nav>
                    <div className="border-t border-gray-200 p-4">
                        <button className="flex items-center w-full px-2 py-2 text-sm font-medium text-gray-600 hover:bg-gray-50 hover:text-gray-900 rounded-md transition-colors">
                            <LogOut className="mr-3 h-5 w-5" />
                            Sign out
                        </button>
                    </div>
                </div>
            </div>

            {/* Main content */}
            <div className="lg:pl-64">
                {/* Top header */}
                <div className="sticky top-0 z-40 flex h-16 shrink-0 items-center gap-x-4 border-b border-gray-200 bg-white px-4 shadow-sm sm:gap-x-6 sm:px-6 lg:px-8">
                    <button
                        type="button"
                        className="-m-2.5 p-2.5 text-gray-700 lg:hidden"
                        onClick={() => setSidebarOpen(true)}
                    >
                        <Menu className="h-6 w-6" />
                    </button>

                    <div className="flex flex-1 gap-x-4 self-stretch lg:gap-x-6">
                        <div className="flex flex-1"></div>
                        <div className="flex items-center gap-x-4 lg:gap-x-6">
                            {/* Notifications */}
                            <button className="relative p-2 text-gray-400 hover:text-gray-500">
                                <Bell className="h-6 w-6" />
                                <span className="absolute top-1 right-1 block h-2 w-2 rounded-full bg-red-400"></span>
                            </button>

                            {/* Profile dropdown */}
                            <div className="relative">
                                <button className="flex items-center gap-x-4 text-sm font-medium text-gray-700 hover:text-gray-900">
                                    <div className="h-8 w-8 rounded-full bg-gray-300 flex items-center justify-center">
                                        <User className="h-5 w-5 text-gray-600" />
                                    </div>
                                    <span className="hidden lg:flex lg:items-center">
                                        John Doe
                                    </span>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Page content */}
                <main className="py-6">
                    <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
                        {children}
                    </div>
                </main>
            </div>
        </div>
    )
}
