'use client'

import { useState } from 'react'
import {
    Plus,
    Search,
    Filter,
    Grid,
    List,
    Share2,
    Edit,
    Trash2,
    Heart,
    Eye,
    ShoppingCart,
    Star,
    Users,
    Lock,
    Globe,
    Calendar,
    MoreVertical,
    Copy,
    Download,
    Settings
} from 'lucide-react'

const mockCollections = [
    {
        id: 1,
        name: 'Summer Collection 2024',
        description: 'Perfect summer dresses and accessories',
        image: 'https://images.unsplash.com/photo-1496747611176-843222e1e57c?w=400&h=300&fit=crop',
        productCount: 24,
        isPublic: true,
        isShared: true,
        sharedWith: ['john@example.com', 'sarah@example.com'],
        createdAt: '2024-12-15T10:00:00Z',
        updatedAt: '2024-12-19T14:30:00Z',
        tags: ['summer', 'dresses', 'accessories'],
        coverColor: 'bg-gradient-to-br from-pink-400 to-orange-400'
    },
    {
        id: 2,
        name: 'Red Dress Inspiration',
        description: 'Beautiful red dresses for special occasions',
        image: 'https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?w=400&h=300&fit=crop',
        productCount: 12,
        isPublic: false,
        isShared: false,
        sharedWith: [],
        createdAt: '2024-12-18T09:00:00Z',
        updatedAt: '2024-12-19T16:45:00Z',
        tags: ['red', 'dresses', 'formal'],
        coverColor: 'bg-gradient-to-br from-red-400 to-pink-400'
    },
    {
        id: 3,
        name: 'Casual Weekend Looks',
        description: 'Comfortable and stylish casual wear',
        image: 'https://images.unsplash.com/photo-1434389677669-e08b4cac3105?w=400&h=300&fit=crop',
        productCount: 18,
        isPublic: true,
        isShared: true,
        sharedWith: ['team@company.com'],
        createdAt: '2024-12-10T11:00:00Z',
        updatedAt: '2024-12-17T13:20:00Z',
        tags: ['casual', 'weekend', 'comfortable'],
        coverColor: 'bg-gradient-to-br from-blue-400 to-purple-400'
    },
    {
        id: 4,
        name: 'Winter Essentials',
        description: 'Warm and cozy winter clothing',
        image: 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400&h=300&fit=crop',
        productCount: 31,
        isPublic: false,
        isShared: false,
        sharedWith: [],
        createdAt: '2024-12-05T08:00:00Z',
        updatedAt: '2024-12-16T10:15:00Z',
        tags: ['winter', 'warm', 'cozy'],
        coverColor: 'bg-gradient-to-br from-gray-400 to-blue-400'
    }
]

const mockProducts = [
    {
        id: 1,
        name: 'Red Summer Dress',
        price: 89.99,
        image: 'https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?w=300&h=400&fit=crop',
        brand: 'Fashion Brand',
        rating: 4.5,
        reviews: 128,
        inStock: true
    },
    {
        id: 2,
        name: 'Floral Print Dress',
        price: 75.50,
        image: 'https://images.unsplash.com/photo-1496747611176-843222e1e57c?w=300&h=400&fit=crop',
        brand: 'Style Co',
        rating: 4.2,
        reviews: 89,
        inStock: true
    },
    {
        id: 3,
        name: 'Casual Red Top',
        price: 45.00,
        image: 'https://images.unsplash.com/photo-1434389677669-e08b4cac3105?w=300&h=400&fit=crop',
        brand: 'Casual Wear',
        rating: 4.0,
        reviews: 67,
        inStock: false
    }
]

export default function CollectionsPage() {
    const [activeTab, setActiveTab] = useState('collections')
    const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
    const [showCreateModal, setShowCreateModal] = useState(false)
    const [showShareModal, setShowShareModal] = useState(false)
    const [selectedCollection, setSelectedCollection] = useState<any>(null)
    const [searchQuery, setSearchQuery] = useState('')
    const [filterVisibility, setFilterVisibility] = useState<'all' | 'public' | 'private'>('all')

    const filteredCollections = mockCollections.filter(collection => {
        const matchesSearch = collection.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
            collection.description.toLowerCase().includes(searchQuery.toLowerCase())
        const matchesVisibility = filterVisibility === 'all' ||
            (filterVisibility === 'public' && collection.isPublic) ||
            (filterVisibility === 'private' && !collection.isPublic)
        return matchesSearch && matchesVisibility
    })

    const handleCreateCollection = () => {
        setShowCreateModal(true)
    }

    const handleShareCollection = (collection: any) => {
        setSelectedCollection(collection)
        setShowShareModal(true)
    }

    const handleDeleteCollection = (collectionId: number) => {
        // In real app, would call API to delete
        console.log('Delete collection:', collectionId)
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900">Collections & Boards</h1>
                    <p className="text-gray-600">Organize and share your favorite products</p>
                </div>
                <button
                    onClick={handleCreateCollection}
                    className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center"
                >
                    <Plus className="h-4 w-4 mr-2" />
                    Create Collection
                </button>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-white p-6 rounded-lg shadow">
                    <div className="flex items-center">
                        <Heart className="h-8 w-8 text-red-600" />
                        <div className="ml-4">
                            <p className="text-sm font-medium text-gray-600">Total Collections</p>
                            <p className="text-2xl font-bold text-gray-900">{mockCollections.length}</p>
                        </div>
                    </div>
                </div>
                <div className="bg-white p-6 rounded-lg shadow">
                    <div className="flex items-center">
                        <Globe className="h-8 w-8 text-green-600" />
                        <div className="ml-4">
                            <p className="text-sm font-medium text-gray-600">Public Collections</p>
                            <p className="text-2xl font-bold text-gray-900">
                                {mockCollections.filter(c => c.isPublic).length}
                            </p>
                        </div>
                    </div>
                </div>
                <div className="bg-white p-6 rounded-lg shadow">
                    <div className="flex items-center">
                        <Users className="h-8 w-8 text-blue-600" />
                        <div className="ml-4">
                            <p className="text-sm font-medium text-gray-600">Shared Collections</p>
                            <p className="text-2xl font-bold text-gray-900">
                                {mockCollections.filter(c => c.isShared).length}
                            </p>
                        </div>
                    </div>
                </div>
                <div className="bg-white p-6 rounded-lg shadow">
                    <div className="flex items-center">
                        <ShoppingCart className="h-8 w-8 text-purple-600" />
                        <div className="ml-4">
                            <p className="text-sm font-medium text-gray-600">Total Products</p>
                            <p className="text-2xl font-bold text-gray-900">
                                {mockCollections.reduce((sum, c) => sum + c.productCount, 0)}
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Tabs */}
            <div className="border-b border-gray-200">
                <nav className="-mb-px flex space-x-8">
                    <button
                        onClick={() => setActiveTab('collections')}
                        className={`py-2 px-1 border-b-2 font-medium text-sm ${activeTab === 'collections'
                                ? 'border-blue-500 text-blue-600'
                                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                            }`}
                    >
                        Collections
                    </button>
                    <button
                        onClick={() => setActiveTab('boards')}
                        className={`py-2 px-1 border-b-2 font-medium text-sm ${activeTab === 'boards'
                                ? 'border-blue-500 text-blue-600'
                                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                            }`}
                    >
                        Boards
                    </button>
                </nav>
            </div>

            {/* Collections Tab */}
            {activeTab === 'collections' && (
                <div className="space-y-6">
                    {/* Search and Filters */}
                    <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                            <div className="relative">
                                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                                <input
                                    type="text"
                                    placeholder="Search collections..."
                                    value={searchQuery}
                                    onChange={(e) => setSearchQuery(e.target.value)}
                                    className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                />
                            </div>
                            <select
                                value={filterVisibility}
                                onChange={(e) => setFilterVisibility(e.target.value as any)}
                                className="border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                            >
                                <option value="all">All Collections</option>
                                <option value="public">Public Only</option>
                                <option value="private">Private Only</option>
                            </select>
                        </div>
                        <div className="flex items-center space-x-2">
                            <button
                                onClick={() => setViewMode('grid')}
                                className={`p-2 rounded ${viewMode === 'grid' ? 'bg-blue-100 text-blue-600' : 'text-gray-400'}`}
                            >
                                <Grid className="h-4 w-4" />
                            </button>
                            <button
                                onClick={() => setViewMode('list')}
                                className={`p-2 rounded ${viewMode === 'list' ? 'bg-blue-100 text-blue-600' : 'text-gray-400'}`}
                            >
                                <List className="h-4 w-4" />
                            </button>
                        </div>
                    </div>

                    {/* Collections Grid */}
                    <div className={`${viewMode === 'grid' ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6' : 'space-y-4'}`}>
                        {filteredCollections.map((collection) => (
                            <div
                                key={collection.id}
                                className={`bg-white rounded-lg shadow hover:shadow-md transition-shadow ${viewMode === 'list' ? 'flex space-x-4 p-4' : 'p-4'
                                    }`}
                            >
                                <div className={`${viewMode === 'list' ? 'w-48 flex-shrink-0' : 'mb-4'}`}>
                                    <div className={`relative h-48 rounded-lg overflow-hidden ${collection.coverColor}`}>
                                        <img
                                            src={collection.image}
                                            alt={collection.name}
                                            className="w-full h-full object-cover"
                                        />
                                        <div className="absolute top-2 right-2 flex space-x-1">
                                            {collection.isPublic ? (
                                                <Globe className="h-4 w-4 text-white" />
                                            ) : (
                                                <Lock className="h-4 w-4 text-white" />
                                            )}
                                            {collection.isShared && (
                                                <Users className="h-4 w-4 text-white" />
                                            )}
                                        </div>
                                    </div>
                                </div>

                                <div className="flex-1">
                                    <div className="flex items-start justify-between mb-2">
                                        <h3 className="font-medium text-gray-900">{collection.name}</h3>
                                        <div className="flex items-center space-x-1">
                                            <button
                                                onClick={() => handleShareCollection(collection)}
                                                className="p-1 text-gray-400 hover:text-gray-600"
                                            >
                                                <Share2 className="h-4 w-4" />
                                            </button>
                                            <button className="p-1 text-gray-400 hover:text-gray-600">
                                                <Edit className="h-4 w-4" />
                                            </button>
                                            <button
                                                onClick={() => handleDeleteCollection(collection.id)}
                                                className="p-1 text-gray-400 hover:text-red-600"
                                            >
                                                <Trash2 className="h-4 w-4" />
                                            </button>
                                        </div>
                                    </div>

                                    <p className="text-sm text-gray-500 mb-3">{collection.description}</p>

                                    <div className="flex items-center justify-between mb-3">
                                        <span className="text-sm text-gray-600">
                                            {collection.productCount} products
                                        </span>
                                        <div className="flex items-center space-x-2">
                                            {collection.tags.slice(0, 2).map((tag) => (
                                                <span
                                                    key={tag}
                                                    className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full"
                                                >
                                                    {tag}
                                                </span>
                                            ))}
                                            {collection.tags.length > 2 && (
                                                <span className="text-xs text-gray-500">
                                                    +{collection.tags.length - 2}
                                                </span>
                                            )}
                                        </div>
                                    </div>

                                    <div className="flex items-center justify-between text-xs text-gray-500">
                                        <span>Updated {new Date(collection.updatedAt).toLocaleDateString()}</span>
                                        {collection.sharedWith.length > 0 && (
                                            <span>Shared with {collection.sharedWith.length} people</span>
                                        )}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Boards Tab */}
            {activeTab === 'boards' && (
                <div className="space-y-6">
                    <div className="text-center py-12">
                        <div className="bg-gray-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                            <Settings className="h-8 w-8 text-gray-400" />
                        </div>
                        <h3 className="text-lg font-medium text-gray-900 mb-2">Boards Coming Soon</h3>
                        <p className="text-gray-600">Advanced board functionality will be available in the next update.</p>
                    </div>
                </div>
            )}

            {/* Create Collection Modal */}
            {showCreateModal && (
                <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
                    <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
                        <div className="mt-3">
                            <h3 className="text-lg font-medium text-gray-900 mb-4">Create New Collection</h3>
                            <div className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Collection Name
                                    </label>
                                    <input
                                        type="text"
                                        className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                        placeholder="Enter collection name"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Description
                                    </label>
                                    <textarea
                                        className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                        rows={3}
                                        placeholder="Describe your collection"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Visibility
                                    </label>
                                    <select className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500">
                                        <option value="private">Private</option>
                                        <option value="public">Public</option>
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Tags
                                    </label>
                                    <input
                                        type="text"
                                        className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                        placeholder="Enter tags separated by commas"
                                    />
                                </div>
                            </div>
                            <div className="mt-6 flex justify-end space-x-3">
                                <button
                                    onClick={() => setShowCreateModal(false)}
                                    className="px-4 py-2 text-gray-500 hover:text-gray-700"
                                >
                                    Cancel
                                </button>
                                <button className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">
                                    Create Collection
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Share Collection Modal */}
            {showShareModal && selectedCollection && (
                <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
                    <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
                        <div className="mt-3">
                            <h3 className="text-lg font-medium text-gray-900 mb-4">Share Collection</h3>
                            <div className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Collection
                                    </label>
                                    <div className="p-3 bg-gray-50 rounded-md">
                                        <p className="font-medium">{selectedCollection.name}</p>
                                        <p className="text-sm text-gray-500">{selectedCollection.description}</p>
                                    </div>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Share with (email addresses)
                                    </label>
                                    <textarea
                                        className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                        rows={3}
                                        placeholder="Enter email addresses separated by commas"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Permission
                                    </label>
                                    <select className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500">
                                        <option value="view">View only</option>
                                        <option value="edit">Can edit</option>
                                        <option value="admin">Admin access</option>
                                    </select>
                                </div>
                                <div className="flex items-center space-x-2">
                                    <input type="checkbox" id="public-link" className="rounded border-gray-300" />
                                    <label htmlFor="public-link" className="text-sm text-gray-700">
                                        Create public link
                                    </label>
                                </div>
                            </div>
                            <div className="mt-6 flex justify-end space-x-3">
                                <button
                                    onClick={() => setShowShareModal(false)}
                                    className="px-4 py-2 text-gray-500 hover:text-gray-700"
                                >
                                    Cancel
                                </button>
                                <button className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">
                                    Share Collection
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}
