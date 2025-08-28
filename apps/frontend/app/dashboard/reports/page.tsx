'use client'

import { useState } from 'react'
import {
    TrendingUp,
    TrendingDown,
    Users,
    Search,
    ShoppingCart,
    Eye,
    Calendar,
    Download,
    Filter,
    BarChart3,
    PieChart,
    Activity,
    Target,
    Clock,
    Star,
    DollarSign
} from 'lucide-react'

// Mock data for charts
const searchTrends = [
    { date: '2024-12-13', searches: 1247, conversions: 89 },
    { date: '2024-12-14', searches: 1356, conversions: 102 },
    { date: '2024-12-15', searches: 1189, conversions: 76 },
    { date: '2024-12-16', searches: 1423, conversions: 113 },
    { date: '2024-12-17', searches: 1567, conversions: 134 },
    { date: '2024-12-18', searches: 1389, conversions: 98 },
    { date: '2024-12-19', searches: 1523, conversions: 127 }
]

const topSearches = [
    { query: 'red dress', count: 234, conversionRate: 12.5 },
    { query: 'summer dress', count: 189, conversionRate: 8.9 },
    { query: 'casual top', count: 156, conversionRate: 15.2 },
    { query: 'winter coat', count: 134, conversionRate: 22.1 },
    { query: 'accessories', count: 98, conversionRate: 6.7 }
]

const categoryPerformance = [
    { category: 'Dresses', searches: 456, conversions: 67, revenue: 12450 },
    { category: 'Tops', searches: 389, conversions: 45, revenue: 8920 },
    { category: 'Outerwear', searches: 234, conversions: 38, revenue: 15670 },
    { category: 'Accessories', searches: 178, conversions: 23, revenue: 3450 },
    { category: 'Shoes', searches: 145, conversions: 19, revenue: 5670 }
]

const userBehavior = [
    { metric: 'Average Session Duration', value: '4m 32s', change: '+12%', trend: 'up' },
    { metric: 'Pages per Session', value: '3.8', change: '+8%', trend: 'up' },
    { metric: 'Bounce Rate', value: '34.2%', change: '-5%', trend: 'down' },
    { metric: 'Return Rate', value: '67.8%', change: '+15%', trend: 'up' }
]

export default function ReportsPage() {
    const [timeRange, setTimeRange] = useState('7d')
    const [selectedMetric, setSelectedMetric] = useState('searches')

    const getMetricIcon = (metric: string) => {
        switch (metric) {
            case 'searches':
                return <Search className="h-5 w-5" />
            case 'conversions':
                return <ShoppingCart className="h-5 w-5" />
            case 'revenue':
                return <DollarSign className="h-5 w-5" />
            case 'users':
                return <Users className="h-5 w-5" />
            default:
                return <Activity className="h-5 w-5" />
        }
    }

    const getTrendIcon = (trend: string) => {
        return trend === 'up' ?
            <TrendingUp className="h-4 w-4 text-green-500" /> :
            <TrendingDown className="h-4 w-4 text-red-500" />
    }

    const getTrendColor = (trend: string) => {
        return trend === 'up' ? 'text-green-600' : 'text-red-600'
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900">Analytics & Reports</h1>
                    <p className="text-gray-600">Track performance and insights across your visual search platform</p>
                </div>
                <div className="flex items-center space-x-4">
                    <select
                        value={timeRange}
                        onChange={(e) => setTimeRange(e.target.value)}
                        className="border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                        <option value="24h">Last 24 hours</option>
                        <option value="7d">Last 7 days</option>
                        <option value="30d">Last 30 days</option>
                        <option value="90d">Last 90 days</option>
                    </select>
                    <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center">
                        <Download className="h-4 w-4 mr-2" />
                        Export Report
                    </button>
                </div>
            </div>

            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="bg-white p-6 rounded-lg shadow">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm font-medium text-gray-600">Total Searches</p>
                            <p className="text-2xl font-bold text-gray-900">9,689</p>
                            <p className="text-sm text-green-600 flex items-center mt-1">
                                <TrendingUp className="h-4 w-4 mr-1" />
                                +12.5% from last period
                            </p>
                        </div>
                        <div className="p-3 bg-blue-100 rounded-lg">
                            <Search className="h-8 w-8 text-blue-600" />
                        </div>
                    </div>
                </div>

                <div className="bg-white p-6 rounded-lg shadow">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm font-medium text-gray-600">Conversions</p>
                            <p className="text-2xl font-bold text-gray-900">739</p>
                            <p className="text-sm text-green-600 flex items-center mt-1">
                                <TrendingUp className="h-4 w-4 mr-1" />
                                +8.3% from last period
                            </p>
                        </div>
                        <div className="p-3 bg-green-100 rounded-lg">
                            <ShoppingCart className="h-8 w-8 text-green-600" />
                        </div>
                    </div>
                </div>

                <div className="bg-white p-6 rounded-lg shadow">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm font-medium text-gray-600">Conversion Rate</p>
                            <p className="text-2xl font-bold text-gray-900">7.6%</p>
                            <p className="text-sm text-red-600 flex items-center mt-1">
                                <TrendingDown className="h-4 w-4 mr-1" />
                                -2.1% from last period
                            </p>
                        </div>
                        <div className="p-3 bg-purple-100 rounded-lg">
                            <Target className="h-8 w-8 text-purple-600" />
                        </div>
                    </div>
                </div>

                <div className="bg-white p-6 rounded-lg shadow">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm font-medium text-gray-600">Revenue</p>
                            <p className="text-2xl font-bold text-gray-900">$46,120</p>
                            <p className="text-sm text-green-600 flex items-center mt-1">
                                <TrendingUp className="h-4 w-4 mr-1" />
                                +15.2% from last period
                            </p>
                        </div>
                        <div className="p-3 bg-yellow-100 rounded-lg">
                            <DollarSign className="h-8 w-8 text-yellow-600" />
                        </div>
                    </div>
                </div>
            </div>

            {/* Charts Section */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Search Trends Chart */}
                <div className="bg-white p-6 rounded-lg shadow">
                    <div className="flex items-center justify-between mb-6">
                        <h3 className="text-lg font-medium text-gray-900">Search Trends</h3>
                        <div className="flex items-center space-x-2">
                            <button
                                onClick={() => setSelectedMetric('searches')}
                                className={`px-3 py-1 rounded-md text-sm font-medium ${selectedMetric === 'searches'
                                        ? 'bg-blue-100 text-blue-700'
                                        : 'text-gray-500 hover:text-gray-700'
                                    }`}
                            >
                                Searches
                            </button>
                            <button
                                onClick={() => setSelectedMetric('conversions')}
                                className={`px-3 py-1 rounded-md text-sm font-medium ${selectedMetric === 'conversions'
                                        ? 'bg-blue-100 text-blue-700'
                                        : 'text-gray-500 hover:text-gray-700'
                                    }`}
                            >
                                Conversions
                            </button>
                        </div>
                    </div>

                    {/* Mock Chart */}
                    <div className="h-64 bg-gray-50 rounded-lg flex items-end justify-between p-4">
                        {searchTrends.map((day, index) => (
                            <div key={index} className="flex flex-col items-center">
                                <div
                                    className="bg-blue-500 rounded-t w-8 mb-2"
                                    style={{
                                        height: `${(day[selectedMetric as keyof typeof day] as number) / 20}px`
                                    }}
                                ></div>
                                <span className="text-xs text-gray-500">
                                    {new Date(day.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                                </span>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Category Performance */}
                <div className="bg-white p-6 rounded-lg shadow">
                    <h3 className="text-lg font-medium text-gray-900 mb-6">Category Performance</h3>
                    <div className="space-y-4">
                        {categoryPerformance.map((category, index) => (
                            <div key={index} className="flex items-center justify-between">
                                <div className="flex items-center space-x-3">
                                    <div className="w-3 h-3 rounded-full bg-blue-500"></div>
                                    <span className="text-sm font-medium text-gray-900">{category.category}</span>
                                </div>
                                <div className="text-right">
                                    <p className="text-sm font-medium text-gray-900">${category.revenue.toLocaleString()}</p>
                                    <p className="text-xs text-gray-500">{category.conversions} conversions</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Detailed Analytics */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Top Searches */}
                <div className="bg-white p-6 rounded-lg shadow">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Top Searches</h3>
                    <div className="space-y-3">
                        {topSearches.map((search, index) => (
                            <div key={index} className="flex items-center justify-between">
                                <div className="flex-1">
                                    <p className="text-sm font-medium text-gray-900">{search.query}</p>
                                    <p className="text-xs text-gray-500">{search.count} searches</p>
                                </div>
                                <div className="text-right">
                                    <p className="text-sm font-medium text-gray-900">{search.conversionRate}%</p>
                                    <p className="text-xs text-gray-500">conversion</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* User Behavior */}
                <div className="bg-white p-6 rounded-lg shadow">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">User Behavior</h3>
                    <div className="space-y-4">
                        {userBehavior.map((metric, index) => (
                            <div key={index} className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm font-medium text-gray-900">{metric.metric}</p>
                                    <p className="text-xs text-gray-500">{metric.change} from last period</p>
                                </div>
                                <div className="text-right">
                                    <p className="text-sm font-bold text-gray-900">{metric.value}</p>
                                    <div className="flex items-center justify-end">
                                        {getTrendIcon(metric.trend)}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Performance Insights */}
                <div className="bg-white p-6 rounded-lg shadow">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Performance Insights</h3>
                    <div className="space-y-4">
                        <div className="p-4 bg-green-50 rounded-lg">
                            <div className="flex items-center space-x-2 mb-2">
                                <TrendingUp className="h-4 w-4 text-green-600" />
                                <span className="text-sm font-medium text-green-800">Strong Performance</span>
                            </div>
                            <p className="text-sm text-green-700">
                                Search volume increased by 12.5% this week, with strong conversion rates in the dresses category.
                            </p>
                        </div>

                        <div className="p-4 bg-yellow-50 rounded-lg">
                            <div className="flex items-center space-x-2 mb-2">
                                <Clock className="h-4 w-4 text-yellow-600" />
                                <span className="text-sm font-medium text-yellow-800">Optimization Opportunity</span>
                            </div>
                            <p className="text-sm text-yellow-700">
                                Accessories category shows low conversion rates. Consider improving product images and descriptions.
                            </p>
                        </div>

                        <div className="p-4 bg-blue-50 rounded-lg">
                            <div className="flex items-center space-x-2 mb-2">
                                <Users className="h-4 w-4 text-blue-600" />
                                <span className="text-sm font-medium text-blue-800">User Engagement</span>
                            </div>
                            <p className="text-sm text-blue-700">
                                Average session duration increased to 4m 32s, indicating improved user experience.
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Additional Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="bg-white p-6 rounded-lg shadow">
                    <div className="flex items-center space-x-3">
                        <div className="p-2 bg-red-100 rounded-lg">
                            <Eye className="h-6 w-6 text-red-600" />
                        </div>
                        <div>
                            <p className="text-sm font-medium text-gray-600">Unique Visitors</p>
                            <p className="text-xl font-bold text-gray-900">3,456</p>
                        </div>
                    </div>
                </div>

                <div className="bg-white p-6 rounded-lg shadow">
                    <div className="flex items-center space-x-3">
                        <div className="p-2 bg-purple-100 rounded-lg">
                            <Star className="h-6 w-6 text-purple-600" />
                        </div>
                        <div>
                            <p className="text-sm font-medium text-gray-600">Avg. Rating</p>
                            <p className="text-xl font-bold text-gray-900">4.6/5</p>
                        </div>
                    </div>
                </div>

                <div className="bg-white p-6 rounded-lg shadow">
                    <div className="flex items-center space-x-3">
                        <div className="p-2 bg-green-100 rounded-lg">
                            <Activity className="h-6 w-6 text-green-600" />
                        </div>
                        <div>
                            <p className="text-sm font-medium text-gray-600">Active Users</p>
                            <p className="text-xl font-bold text-gray-900">1,234</p>
                        </div>
                    </div>
                </div>

                <div className="bg-white p-6 rounded-lg shadow">
                    <div className="flex items-center space-x-3">
                        <div className="p-2 bg-orange-100 rounded-lg">
                            <BarChart3 className="h-6 w-6 text-orange-600" />
                        </div>
                        <div>
                            <p className="text-sm font-medium text-gray-600">Search Accuracy</p>
                            <p className="text-xl font-bold text-gray-900">94.2%</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}
