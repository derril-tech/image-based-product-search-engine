'use client'

import { useState } from 'react'
import {
    Upload,
    Database,
    Settings,
    Play,
    Pause,
    Trash2,
    RefreshCw,
    CheckCircle,
    AlertCircle,
    Clock,
    Plus,
    ExternalLink,
    FileText,
    ShoppingCart,
    Globe,
    Zap
} from 'lucide-react'

const connectors = [
    {
        id: 'shopify',
        name: 'Shopify',
        description: 'Import products from your Shopify store',
        icon: ShoppingCart,
        status: 'connected',
        lastSync: '2 hours ago',
        productCount: 1247,
        color: 'bg-green-100 text-green-800'
    },
    {
        id: 'bigcommerce',
        name: 'BigCommerce',
        description: 'Connect your BigCommerce store',
        icon: Globe,
        status: 'disconnected',
        lastSync: 'Never',
        productCount: 0,
        color: 'bg-gray-100 text-gray-800'
    },
    {
        id: 'woocommerce',
        name: 'WooCommerce',
        description: 'Import from WordPress WooCommerce',
        icon: Zap,
        status: 'connected',
        lastSync: '1 day ago',
        productCount: 892,
        color: 'bg-blue-100 text-blue-800'
    },
    {
        id: 'csv',
        name: 'CSV Import',
        description: 'Upload product data via CSV file',
        icon: FileText,
        status: 'available',
        lastSync: '3 days ago',
        productCount: 156,
        color: 'bg-purple-100 text-purple-800'
    }
]

const importJobs = [
    {
        id: 'job-1',
        name: 'Shopify Full Sync',
        status: 'completed',
        progress: 100,
        productsImported: 1247,
        startedAt: '2024-12-19T10:00:00Z',
        completedAt: '2024-12-19T10:15:00Z',
        connector: 'shopify'
    },
    {
        id: 'job-2',
        name: 'WooCommerce Update',
        status: 'running',
        progress: 65,
        productsImported: 580,
        startedAt: '2024-12-19T11:30:00Z',
        connector: 'woocommerce'
    },
    {
        id: 'job-3',
        name: 'CSV Import - New Products',
        status: 'failed',
        progress: 45,
        productsImported: 67,
        startedAt: '2024-12-19T09:00:00Z',
        error: 'Invalid CSV format on line 156',
        connector: 'csv'
    }
]

export default function CatalogPage() {
    const [activeTab, setActiveTab] = useState('connectors')
    const [showConnectModal, setShowConnectModal] = useState(false)
    const [selectedConnector, setSelectedConnector] = useState(null)

    const getStatusIcon = (status: string) => {
        switch (status) {
            case 'completed':
                return <CheckCircle className="h-5 w-5 text-green-500" />
            case 'running':
                return <RefreshCw className="h-5 w-5 text-blue-500 animate-spin" />
            case 'failed':
                return <AlertCircle className="h-5 w-5 text-red-500" />
            case 'pending':
                return <Clock className="h-5 w-5 text-yellow-500" />
            default:
                return <Clock className="h-5 w-5 text-gray-500" />
        }
    }

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'completed':
                return 'bg-green-100 text-green-800'
            case 'running':
                return 'bg-blue-100 text-blue-800'
            case 'failed':
                return 'bg-red-100 text-red-800'
            case 'pending':
                return 'bg-yellow-100 text-yellow-800'
            default:
                return 'bg-gray-100 text-gray-800'
        }
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900">Catalog Management</h1>
                    <p className="text-gray-600">Import and manage your product catalog from various sources</p>
                </div>
                <button
                    onClick={() => setShowConnectModal(true)}
                    className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center"
                >
                    <Plus className="h-4 w-4 mr-2" />
                    Add Connector
                </button>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-white p-6 rounded-lg shadow">
                    <div className="flex items-center">
                        <Database className="h-8 w-8 text-blue-600" />
                        <div className="ml-4">
                            <p className="text-sm font-medium text-gray-600">Total Products</p>
                            <p className="text-2xl font-bold text-gray-900">2,295</p>
                        </div>
                    </div>
                </div>
                <div className="bg-white p-6 rounded-lg shadow">
                    <div className="flex items-center">
                        <CheckCircle className="h-8 w-8 text-green-600" />
                        <div className="ml-4">
                            <p className="text-sm font-medium text-gray-600">Active Connectors</p>
                            <p className="text-2xl font-bold text-gray-900">3</p>
                        </div>
                    </div>
                </div>
                <div className="bg-white p-6 rounded-lg shadow">
                    <div className="flex items-center">
                        <RefreshCw className="h-8 w-8 text-blue-600" />
                        <div className="ml-4">
                            <p className="text-sm font-medium text-gray-600">Last Sync</p>
                            <p className="text-2xl font-bold text-gray-900">2h ago</p>
                        </div>
                    </div>
                </div>
                <div className="bg-white p-6 rounded-lg shadow">
                    <div className="flex items-center">
                        <AlertCircle className="h-8 w-8 text-yellow-600" />
                        <div className="ml-4">
                            <p className="text-sm font-medium text-gray-600">Sync Errors</p>
                            <p className="text-2xl font-bold text-gray-900">1</p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Tabs */}
            <div className="border-b border-gray-200">
                <nav className="-mb-px flex space-x-8">
                    <button
                        onClick={() => setActiveTab('connectors')}
                        className={`py-2 px-1 border-b-2 font-medium text-sm ${activeTab === 'connectors'
                                ? 'border-blue-500 text-blue-600'
                                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                            }`}
                    >
                        Connectors
                    </button>
                    <button
                        onClick={() => setActiveTab('imports')}
                        className={`py-2 px-1 border-b-2 font-medium text-sm ${activeTab === 'imports'
                                ? 'border-blue-500 text-blue-600'
                                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                            }`}
                    >
                        Import Jobs
                    </button>
                    <button
                        onClick={() => setActiveTab('settings')}
                        className={`py-2 px-1 border-b-2 font-medium text-sm ${activeTab === 'settings'
                                ? 'border-blue-500 text-blue-600'
                                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                            }`}
                    >
                        Settings
                    </button>
                </nav>
            </div>

            {/* Connectors Tab */}
            {activeTab === 'connectors' && (
                <div className="space-y-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {connectors.map((connector) => (
                            <div key={connector.id} className="bg-white rounded-lg shadow p-6">
                                <div className="flex items-start justify-between">
                                    <div className="flex items-center">
                                        <div className="p-2 bg-gray-100 rounded-lg">
                                            <connector.icon className="h-6 w-6 text-gray-600" />
                                        </div>
                                        <div className="ml-4">
                                            <h3 className="text-lg font-medium text-gray-900">{connector.name}</h3>
                                            <p className="text-sm text-gray-500">{connector.description}</p>
                                        </div>
                                    </div>
                                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${connector.color}`}>
                                        {connector.status}
                                    </span>
                                </div>

                                <div className="mt-4 space-y-3">
                                    <div className="flex justify-between text-sm">
                                        <span className="text-gray-500">Products:</span>
                                        <span className="font-medium">{connector.productCount.toLocaleString()}</span>
                                    </div>
                                    <div className="flex justify-between text-sm">
                                        <span className="text-gray-500">Last sync:</span>
                                        <span className="font-medium">{connector.lastSync}</span>
                                    </div>
                                </div>

                                <div className="mt-6 flex space-x-3">
                                    {connector.status === 'connected' ? (
                                        <>
                                            <button className="flex-1 bg-blue-600 text-white px-3 py-2 rounded-md text-sm font-medium hover:bg-blue-700 transition-colors flex items-center justify-center">
                                                <RefreshCw className="h-4 w-4 mr-2" />
                                                Sync Now
                                            </button>
                                            <button className="px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors">
                                                <Settings className="h-4 w-4" />
                                            </button>
                                        </>
                                    ) : connector.status === 'disconnected' ? (
                                        <button className="flex-1 bg-blue-600 text-white px-3 py-2 rounded-md text-sm font-medium hover:bg-blue-700 transition-colors">
                                            Connect
                                        </button>
                                    ) : (
                                        <button className="flex-1 bg-gray-600 text-white px-3 py-2 rounded-md text-sm font-medium hover:bg-gray-700 transition-colors">
                                            Setup
                                        </button>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Import Jobs Tab */}
            {activeTab === 'imports' && (
                <div className="space-y-6">
                    <div className="bg-white shadow rounded-lg">
                        <div className="px-6 py-4 border-b border-gray-200">
                            <h3 className="text-lg font-medium text-gray-900">Recent Import Jobs</h3>
                        </div>
                        <div className="divide-y divide-gray-200">
                            {importJobs.map((job) => (
                                <div key={job.id} className="px-6 py-4">
                                    <div className="flex items-center justify-between">
                                        <div className="flex items-center">
                                            {getStatusIcon(job.status)}
                                            <div className="ml-3">
                                                <p className="text-sm font-medium text-gray-900">{job.name}</p>
                                                <p className="text-sm text-gray-500">
                                                    {job.productsImported} products imported
                                                </p>
                                            </div>
                                        </div>
                                        <div className="flex items-center space-x-3">
                                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(job.status)}`}>
                                                {job.status}
                                            </span>
                                            <div className="flex space-x-2">
                                                {job.status === 'running' && (
                                                    <button className="text-gray-400 hover:text-gray-600">
                                                        <Pause className="h-4 w-4" />
                                                    </button>
                                                )}
                                                <button className="text-gray-400 hover:text-gray-600">
                                                    <Trash2 className="h-4 w-4" />
                                                </button>
                                            </div>
                                        </div>
                                    </div>

                                    {job.status === 'running' && (
                                        <div className="mt-3">
                                            <div className="flex justify-between text-sm text-gray-500 mb-1">
                                                <span>Progress</span>
                                                <span>{job.progress}%</span>
                                            </div>
                                            <div className="w-full bg-gray-200 rounded-full h-2">
                                                <div
                                                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                                                    style={{ width: `${job.progress}%` }}
                                                ></div>
                                            </div>
                                        </div>
                                    )}

                                    {job.error && (
                                        <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-md">
                                            <p className="text-sm text-red-600">{job.error}</p>
                                        </div>
                                    )}

                                    <div className="mt-3 text-sm text-gray-500">
                                        Started: {new Date(job.startedAt).toLocaleString()}
                                        {job.completedAt && (
                                            <span className="ml-4">
                                                Completed: {new Date(job.completedAt).toLocaleString()}
                                            </span>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            )}

            {/* Settings Tab */}
            {activeTab === 'settings' && (
                <div className="space-y-6">
                    <div className="bg-white shadow rounded-lg p-6">
                        <h3 className="text-lg font-medium text-gray-900 mb-4">Import Settings</h3>
                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Auto-sync Interval
                                </label>
                                <select className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500">
                                    <option>Every 6 hours</option>
                                    <option>Every 12 hours</option>
                                    <option>Daily</option>
                                    <option>Weekly</option>
                                    <option>Manual only</option>
                                </select>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Image Processing
                                </label>
                                <div className="space-y-2">
                                    <label className="flex items-center">
                                        <input type="checkbox" className="rounded border-gray-300 text-blue-600 focus:ring-blue-500" defaultChecked />
                                        <span className="ml-2 text-sm text-gray-700">Generate thumbnails</span>
                                    </label>
                                    <label className="flex items-center">
                                        <input type="checkbox" className="rounded border-gray-300 text-blue-600 focus:ring-blue-500" defaultChecked />
                                        <span className="ml-2 text-sm text-gray-700">Extract product regions</span>
                                    </label>
                                    <label className="flex items-center">
                                        <input type="checkbox" className="rounded border-gray-300 text-blue-600 focus:ring-blue-500" />
                                        <span className="ml-2 text-sm text-gray-700">Background removal</span>
                                    </label>
                                </div>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Conflict Resolution
                                </label>
                                <select className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500">
                                    <option>Update existing products</option>
                                    <option>Skip existing products</option>
                                    <option>Create duplicates</option>
                                </select>
                            </div>
                        </div>

                        <div className="mt-6">
                            <button className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors">
                                Save Settings
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Connect Modal */}
            {showConnectModal && (
                <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
                    <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
                        <div className="mt-3">
                            <h3 className="text-lg font-medium text-gray-900 mb-4">Connect New Source</h3>
                            <div className="space-y-4">
                                <button className="w-full flex items-center p-3 border border-gray-300 rounded-lg hover:bg-gray-50">
                                    <ShoppingCart className="h-6 w-6 text-green-600 mr-3" />
                                    <div className="text-left">
                                        <p className="font-medium">Shopify</p>
                                        <p className="text-sm text-gray-500">Connect your Shopify store</p>
                                    </div>
                                </button>
                                <button className="w-full flex items-center p-3 border border-gray-300 rounded-lg hover:bg-gray-50">
                                    <Globe className="h-6 w-6 text-blue-600 mr-3" />
                                    <div className="text-left">
                                        <p className="font-medium">BigCommerce</p>
                                        <p className="text-sm text-gray-500">Connect your BigCommerce store</p>
                                    </div>
                                </button>
                                <button className="w-full flex items-center p-3 border border-gray-300 rounded-lg hover:bg-gray-50">
                                    <Zap className="h-6 w-6 text-purple-600 mr-3" />
                                    <div className="text-left">
                                        <p className="font-medium">WooCommerce</p>
                                        <p className="text-sm text-gray-500">Connect your WordPress store</p>
                                    </div>
                                </button>
                                <button className="w-full flex items-center p-3 border border-gray-300 rounded-lg hover:bg-gray-50">
                                    <FileText className="h-6 w-6 text-gray-600 mr-3" />
                                    <div className="text-left">
                                        <p className="font-medium">CSV Upload</p>
                                        <p className="text-sm text-gray-500">Upload product data file</p>
                                    </div>
                                </button>
                            </div>
                            <div className="mt-6 flex justify-end">
                                <button
                                    onClick={() => setShowConnectModal(false)}
                                    className="px-4 py-2 text-gray-500 hover:text-gray-700"
                                >
                                    Cancel
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}
