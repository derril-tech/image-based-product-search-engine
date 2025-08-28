'use client'

import { useState } from 'react'
import { TrendingUp, TrendingDown, Download, Calendar, BarChart3, PieChart, Activity, Target } from 'lucide-react'

interface Metric {
    name: string
    value: string | number
    change: string
    trend: 'up' | 'down' | 'neutral'
    icon?: React.ReactNode
}

interface ChartData {
    label: string
    value: number
    color?: string
}

interface ReportData {
    title: string
    description: string
    metrics: Metric[]
    charts?: {
        type: 'bar' | 'line' | 'pie'
        title: string
        data: ChartData[]
    }[]
    timeRange?: string
}

interface ReportsProps {
    data: ReportData
    onExport?: () => void
    onTimeRangeChange?: (range: string) => void
    className?: string
    showCharts?: boolean
    showMetrics?: boolean
}

export default function Reports({
    data,
    onExport,
    onTimeRangeChange,
    className = '',
    showCharts = true,
    showMetrics = true
}: ReportsProps) {
    const [selectedTimeRange, setSelectedTimeRange] = useState(data.timeRange || '7d')

    const handleTimeRangeChange = (range: string) => {
        setSelectedTimeRange(range)
        onTimeRangeChange?.(range)
    }

    const getTrendIcon = (trend: string) => {
        switch (trend) {
            case 'up':
                return <TrendingUp className="h-4 w-4 text-green-500" />
            case 'down':
                return <TrendingDown className="h-4 w-4 text-red-500" />
            default:
                return <Activity className="h-4 w-4 text-gray-500" />
        }
    }

    const getTrendColor = (trend: string) => {
        switch (trend) {
            case 'up':
                return 'text-green-600'
            case 'down':
                return 'text-red-600'
            default:
                return 'text-gray-600'
        }
    }

    const renderChart = (chart: any) => {
        switch (chart.type) {
            case 'bar':
                return (
                    <div className="h-64 bg-gray-50 rounded-lg flex items-end justify-between p-4">
                        {chart.data.map((item: any, index: number) => (
                            <div key={index} className="flex flex-col items-center">
                                <div
                                    className="bg-blue-500 rounded-t w-8 mb-2"
                                    style={{
                                        height: `${(item.value / Math.max(...chart.data.map((d: any) => d.value))) * 200}px`,
                                        backgroundColor: item.color || '#3B82F6'
                                    }}
                                ></div>
                                <span className="text-xs text-gray-500">{item.label}</span>
                            </div>
                        ))}
                    </div>
                )
            case 'pie':
                return (
                    <div className="h-64 bg-gray-50 rounded-lg flex items-center justify-center p-4">
                        <div className="text-center">
                            <PieChart className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                            <p className="text-sm text-gray-600">Pie chart visualization</p>
                        </div>
                    </div>
                )
            case 'line':
                return (
                    <div className="h-64 bg-gray-50 rounded-lg flex items-center justify-center p-4">
                        <div className="text-center">
                            <Activity className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                            <p className="text-sm text-gray-600">Line chart visualization</p>
                        </div>
                    </div>
                )
            default:
                return null
        }
    }

    return (
        <div className={`space-y-6 ${className}`}>
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold text-gray-900">{data.title}</h2>
                    <p className="text-gray-600">{data.description}</p>
                </div>
                <div className="flex items-center space-x-4">
                    {onTimeRangeChange && (
                        <select
                            value={selectedTimeRange}
                            onChange={(e) => handleTimeRangeChange(e.target.value)}
                            className="border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                            <option value="24h">Last 24 hours</option>
                            <option value="7d">Last 7 days</option>
                            <option value="30d">Last 30 days</option>
                            <option value="90d">Last 90 days</option>
                        </select>
                    )}
                    {onExport && (
                        <button
                            onClick={onExport}
                            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center"
                        >
                            <Download className="h-4 w-4 mr-2" />
                            Export Report
                        </button>
                    )}
                </div>
            </div>

            {/* Metrics */}
            {showMetrics && data.metrics && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    {data.metrics.map((metric, index) => (
                        <div key={index} className="bg-white p-6 rounded-lg shadow">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm font-medium text-gray-600">{metric.name}</p>
                                    <p className="text-2xl font-bold text-gray-900">{metric.value}</p>
                                    <p className={`text-sm flex items-center mt-1 ${getTrendColor(metric.trend)}`}>
                                        {getTrendIcon(metric.trend)}
                                        <span className="ml-1">{metric.change}</span>
                                    </p>
                                </div>
                                {metric.icon && (
                                    <div className="p-3 bg-blue-100 rounded-lg">
                                        {metric.icon}
                                    </div>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {/* Charts */}
            {showCharts && data.charts && data.charts.length > 0 && (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {data.charts.map((chart, index) => (
                        <div key={index} className="bg-white p-6 rounded-lg shadow">
                            <h3 className="text-lg font-medium text-gray-900 mb-4">{chart.title}</h3>
                            {renderChart(chart)}
                        </div>
                    ))}
                </div>
            )}

            {/* Summary Insights */}
            <div className="bg-white p-6 rounded-lg shadow">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Key Insights</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    <div className="p-4 bg-green-50 rounded-lg">
                        <div className="flex items-center space-x-2 mb-2">
                            <TrendingUp className="h-4 w-4 text-green-600" />
                            <span className="text-sm font-medium text-green-800">Strong Performance</span>
                        </div>
                        <p className="text-sm text-green-700">
                            Overall metrics show positive growth trends across all key indicators.
                        </p>
                    </div>

                    <div className="p-4 bg-yellow-50 rounded-lg">
                        <div className="flex items-center space-x-2 mb-2">
                            <Target className="h-4 w-4 text-yellow-600" />
                            <span className="text-sm font-medium text-yellow-800">Optimization Opportunity</span>
                        </div>
                        <p className="text-sm text-yellow-700">
                            Some areas show potential for improvement and optimization.
                        </p>
                    </div>

                    <div className="p-4 bg-blue-50 rounded-lg">
                        <div className="flex items-center space-x-2 mb-2">
                            <BarChart3 className="h-4 w-4 text-blue-600" />
                            <span className="text-sm font-medium text-blue-800">Data Trends</span>
                        </div>
                        <p className="text-sm text-blue-700">
                            Consistent patterns indicate stable performance and user engagement.
                        </p>
                    </div>
                </div>
            </div>

            {/* Recommendations */}
            <div className="bg-white p-6 rounded-lg shadow">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Recommendations</h3>
                <div className="space-y-3">
                    <div className="flex items-start space-x-3">
                        <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
                        <p className="text-sm text-gray-700">
                            Continue monitoring performance metrics to maintain current growth trajectory.
                        </p>
                    </div>
                    <div className="flex items-start space-x-3">
                        <div className="w-2 h-2 bg-green-500 rounded-full mt-2 flex-shrink-0"></div>
                        <p className="text-sm text-gray-700">
                            Consider implementing additional features based on user behavior patterns.
                        </p>
                    </div>
                    <div className="flex items-start space-x-3">
                        <div className="w-2 h-2 bg-yellow-500 rounded-full mt-2 flex-shrink-0"></div>
                        <p className="text-sm text-gray-700">
                            Review and optimize areas showing lower performance metrics.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    )
}
