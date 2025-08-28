'use client'

import { useState, useRef } from 'react'
import {
    Upload,
    Search,
    Filter,
    Grid,
    List,
    Sliders,
    X,
    Heart,
    ShoppingCart,
    Eye,
    Star,
    ChevronDown,
    ChevronUp
} from 'lucide-react'
import SearchStatus from '../../../components/SearchStatus'
import '../../../lib/websocket-mock' // Import mock WebSocket server for testing

const mockResults = [
    {
        id: 1,
        name: 'Red Summer Dress',
        price: 89.99,
        originalPrice: 129.99,
        image: 'https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?w=300&h=400&fit=crop',
        category: 'Dresses',
        brand: 'Fashion Brand',
        rating: 4.5,
        reviews: 128,
        similarity: 0.95,
        inStock: true
    },
    {
        id: 2,
        name: 'Floral Print Dress',
        price: 75.50,
        originalPrice: 95.00,
        image: 'https://images.unsplash.com/photo-1496747611176-843222e1e57c?w=300&h=400&fit=crop',
        category: 'Dresses',
        brand: 'Style Co',
        rating: 4.2,
        reviews: 89,
        similarity: 0.92,
        inStock: true
    },
    {
        id: 3,
        name: 'Casual Red Top',
        price: 45.00,
        originalPrice: 60.00,
        image: 'https://images.unsplash.com/photo-1434389677669-e08b4cac3105?w=300&h=400&fit=crop',
        category: 'Tops',
        brand: 'Casual Wear',
        rating: 4.0,
        reviews: 67,
        similarity: 0.88,
        inStock: false
    },
    {
        id: 4,
        name: 'Red Blouse',
        price: 55.99,
        originalPrice: 75.99,
        image: 'https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=300&h=400&fit=crop',
        category: 'Tops',
        brand: 'Elegant Fashion',
        rating: 4.3,
        reviews: 156,
        similarity: 0.85,
        inStock: true
    },
    {
        id: 5,
        name: 'Red Cardigan',
        price: 65.00,
        originalPrice: 85.00,
        image: 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=300&h=400&fit=crop',
        category: 'Outerwear',
        brand: 'Cozy Knits',
        rating: 4.1,
        reviews: 92,
        similarity: 0.82,
        inStock: true
    },
    {
        id: 6,
        name: 'Red Scarf',
        price: 25.99,
        originalPrice: 35.99,
        image: 'https://images.unsplash.com/photo-1544966503-7cc5ac882d5f?w=300&h=400&fit=crop',
        category: 'Accessories',
        brand: 'Winter Warmth',
        rating: 4.4,
        reviews: 203,
        similarity: 0.78,
        inStock: true
    }
]

const facets = {
    category: [
        { name: 'Dresses', count: 45, selected: false },
        { name: 'Tops', count: 32, selected: false },
        { name: 'Outerwear', count: 18, selected: false },
        { name: 'Accessories', count: 12, selected: false }
    ],
    brand: [
        { name: 'Fashion Brand', count: 23, selected: false },
        { name: 'Style Co', count: 18, selected: false },
        { name: 'Casual Wear', count: 15, selected: false },
        { name: 'Elegant Fashion', count: 12, selected: false }
    ],
    price: [
        { name: 'Under $25', count: 8, selected: false },
        { name: '$25 - $50', count: 25, selected: false },
        { name: '$50 - $100', count: 42, selected: false },
        { name: 'Over $100', count: 15, selected: false }
    ],
    rating: [
        { name: '4+ Stars', count: 78, selected: false },
        { name: '3+ Stars', count: 12, selected: false }
    ]
}

export default function SearchPage() {
    const [searchMode, setSearchMode] = useState<'upload' | 'text'>('upload')
    const [uploadedImage, setUploadedImage] = useState<string | null>(null)
    const [cropArea, setCropArea] = useState({ x: 0, y: 0, width: 100, height: 100 })
    const [isSearching, setIsSearching] = useState(false)
    const [searchResults, setSearchResults] = useState(mockResults)
    const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
    const [showFilters, setShowFilters] = useState(false)
    const [selectedFacets, setSelectedFacets] = useState<{ [key: string]: string[] }>({})
    const [sortBy, setSortBy] = useState('relevance')
    const [currentSearchId, setCurrentSearchId] = useState<string | null>(null)
    const [showSearchStatus, setShowSearchStatus] = useState(false)
    const fileInputRef = useRef<HTMLInputElement>(null)

    const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0]
        if (file) {
            const reader = new FileReader()
            reader.onload = (e) => {
                setUploadedImage(e.target?.result as string)
            }
            reader.readAsDataURL(file)
        }
    }

    const handleSearch = async () => {
        setIsSearching(true)
        setShowSearchStatus(true)

        // Generate a mock search ID
        const searchId = `search_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
        setCurrentSearchId(searchId)

        // Simulate search delay
        await new Promise(resolve => setTimeout(resolve, 2000))
        setIsSearching(false)
        setShowSearchStatus(false)
        setCurrentSearchId(null)
    }

    const handleSearchComplete = (results: any[]) => {
        setSearchResults(results)
        setIsSearching(false)
        setShowSearchStatus(false)
        setCurrentSearchId(null)
    }

    const handleSearchError = (error: string) => {
        console.error('Search error:', error)
        setIsSearching(false)
        setShowSearchStatus(false)
        setCurrentSearchId(null)
    }

    const handleFacetChange = (facetType: string, value: string) => {
        setSelectedFacets(prev => {
            const current = prev[facetType] || []
            const updated = current.includes(value)
                ? current.filter(v => v !== value)
                : [...current, value]
            return {
                ...prev,
                [facetType]: updated
            }
        })
    }

    const clearFilters = () => {
        setSelectedFacets({})
    }

    const getActiveFiltersCount = () => {
        return Object.values(selectedFacets).flat().length
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-2xl font-bold text-gray-900">Visual Search</h1>
                <p className="text-gray-600">Upload an image to find similar products in your catalog</p>
            </div>

            {/* Search Interface */}
            <div className="bg-white rounded-lg shadow p-6">
                {/* Search Mode Toggle */}
                <div className="flex space-x-4 mb-6">
                    <button
                        onClick={() => setSearchMode('upload')}
                        className={`px-4 py-2 rounded-lg font-medium transition-colors ${searchMode === 'upload'
                            ? 'bg-blue-600 text-white'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                            }`}
                    >
                        Upload Image
                    </button>
                    <button
                        onClick={() => setSearchMode('text')}
                        className={`px-4 py-2 rounded-lg font-medium transition-colors ${searchMode === 'text'
                            ? 'bg-blue-600 text-white'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                            }`}
                    >
                        Text Search
                    </button>
                </div>

                {searchMode === 'upload' ? (
                    <div className="space-y-6">
                        {/* Upload Area */}
                        {!uploadedImage ? (
                            <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-400 transition-colors">
                                <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                                <p className="text-lg font-medium text-gray-900 mb-2">Upload an image</p>
                                <p className="text-gray-600 mb-4">Drag and drop or click to browse</p>
                                <button
                                    onClick={() => fileInputRef.current?.click()}
                                    className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                                >
                                    Choose File
                                </button>
                                <input
                                    ref={fileInputRef}
                                    type="file"
                                    accept="image/*"
                                    onChange={handleFileUpload}
                                    className="hidden"
                                />
                            </div>
                        ) : (
                            <div className="space-y-4">
                                {/* Image Preview with Crop */}
                                <div className="relative bg-gray-100 rounded-lg p-4">
                                    <div className="relative inline-block">
                                        <img
                                            src={uploadedImage}
                                            alt="Uploaded"
                                            className="max-w-full h-auto rounded-lg"
                                        />
                                        {/* Crop overlay would go here */}
                                        <div className="absolute inset-0 border-2 border-blue-500 border-dashed pointer-events-none"></div>
                                    </div>
                                    <button
                                        onClick={() => setUploadedImage(null)}
                                        className="absolute top-2 right-2 bg-red-500 text-white p-1 rounded-full hover:bg-red-600"
                                    >
                                        <X className="h-4 w-4" />
                                    </button>
                                </div>

                                {/* Crop Controls */}
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center space-x-4">
                                        <button className="px-3 py-1 border border-gray-300 rounded text-sm hover:bg-gray-50">
                                            Auto Crop
                                        </button>
                                        <button className="px-3 py-1 border border-gray-300 rounded text-sm hover:bg-gray-50">
                                            Manual Crop
                                        </button>
                                    </div>
                                    <button
                                        onClick={handleSearch}
                                        disabled={isSearching}
                                        className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors flex items-center"
                                    >
                                        {isSearching ? (
                                            <>
                                                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                                                Searching...
                                            </>
                                        ) : (
                                            <>
                                                <Search className="h-4 w-4 mr-2" />
                                                Search
                                            </>
                                        )}
                                    </button>
                                </div>
                            </div>
                        )}
                    </div>
                ) : (
                    <div className="space-y-4">
                        <div className="flex space-x-4">
                            <input
                                type="text"
                                placeholder="Describe what you're looking for..."
                                className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                            />
                            <button
                                onClick={handleSearch}
                                disabled={isSearching}
                                className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
                            >
                                {isSearching ? 'Searching...' : 'Search'}
                            </button>
                        </div>
                    </div>
                )}
            </div>

            {/* Search Status */}
            {showSearchStatus && currentSearchId && (
                <SearchStatus
                    searchId={currentSearchId}
                    websocketUrl="ws://localhost:3001/ws/search"
                    onComplete={handleSearchComplete}
                    onError={handleSearchError}
                    className="mb-6"
                />
            )}

            {/* Results Section */}
            {searchResults.length > 0 && (
                <div className="space-y-6">
                    {/* Results Header */}
                    <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                            <h2 className="text-lg font-medium text-gray-900">
                                {searchResults.length} results found
                            </h2>
                            {getActiveFiltersCount() > 0 && (
                                <button
                                    onClick={clearFilters}
                                    className="text-sm text-blue-600 hover:text-blue-700"
                                >
                                    Clear all filters
                                </button>
                            )}
                        </div>
                        <div className="flex items-center space-x-4">
                            {/* Sort */}
                            <select
                                value={sortBy}
                                onChange={(e) => setSortBy(e.target.value)}
                                className="border border-gray-300 rounded-md px-3 py-1 text-sm"
                            >
                                <option value="relevance">Relevance</option>
                                <option value="price-low">Price: Low to High</option>
                                <option value="price-high">Price: High to Low</option>
                                <option value="rating">Rating</option>
                                <option value="newest">Newest</option>
                            </select>

                            {/* View Mode */}
                            <div className="flex border border-gray-300 rounded-md">
                                <button
                                    onClick={() => setViewMode('grid')}
                                    className={`p-2 ${viewMode === 'grid' ? 'bg-blue-600 text-white' : 'text-gray-600'}`}
                                >
                                    <Grid className="h-4 w-4" />
                                </button>
                                <button
                                    onClick={() => setViewMode('list')}
                                    className={`p-2 ${viewMode === 'list' ? 'bg-blue-600 text-white' : 'text-gray-600'}`}
                                >
                                    <List className="h-4 w-4" />
                                </button>
                            </div>

                            {/* Filters Toggle */}
                            <button
                                onClick={() => setShowFilters(!showFilters)}
                                className="flex items-center space-x-2 px-3 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
                            >
                                <Filter className="h-4 w-4" />
                                <span>Filters</span>
                                {getActiveFiltersCount() > 0 && (
                                    <span className="bg-blue-600 text-white text-xs rounded-full px-2 py-1">
                                        {getActiveFiltersCount()}
                                    </span>
                                )}
                            </button>
                        </div>
                    </div>

                    <div className="flex space-x-6">
                        {/* Filters Sidebar */}
                        {showFilters && (
                            <div className="w-64 bg-white rounded-lg shadow p-4 space-y-6">
                                {Object.entries(facets).map(([facetType, facetValues]) => (
                                    <div key={facetType}>
                                        <h3 className="font-medium text-gray-900 mb-3 capitalize">
                                            {facetType}
                                        </h3>
                                        <div className="space-y-2">
                                            {facetValues.map((facet) => (
                                                <label key={facet.name} className="flex items-center">
                                                    <input
                                                        type="checkbox"
                                                        checked={selectedFacets[facetType]?.includes(facet.name) || false}
                                                        onChange={() => handleFacetChange(facetType, facet.name)}
                                                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                                                    />
                                                    <span className="ml-2 text-sm text-gray-700">
                                                        {facet.name}
                                                    </span>
                                                    <span className="ml-auto text-sm text-gray-500">
                                                        ({facet.count})
                                                    </span>
                                                </label>
                                            ))}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}

                        {/* Results Grid */}
                        <div className={`flex-1 ${viewMode === 'grid' ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6' : 'space-y-4'}`}>
                            {searchResults.map((product) => (
                                <div
                                    key={product.id}
                                    className={`bg-white rounded-lg shadow hover:shadow-md transition-shadow ${viewMode === 'list' ? 'flex space-x-4 p-4' : 'p-4'
                                        }`}
                                >
                                    <div className={`${viewMode === 'list' ? 'w-32 flex-shrink-0' : 'mb-4'}`}>
                                        <img
                                            src={product.image}
                                            alt={product.name}
                                            className="w-full h-48 object-cover rounded-lg"
                                        />
                                    </div>

                                    <div className="flex-1">
                                        <div className="flex items-start justify-between mb-2">
                                            <h3 className="font-medium text-gray-900">{product.name}</h3>
                                            <div className="flex items-center space-x-1">
                                                <Star className="h-4 w-4 text-yellow-400 fill-current" />
                                                <span className="text-sm text-gray-600">{product.rating}</span>
                                                <span className="text-sm text-gray-500">({product.reviews})</span>
                                            </div>
                                        </div>

                                        <p className="text-sm text-gray-500 mb-2">{product.brand}</p>

                                        <div className="flex items-center justify-between mb-3">
                                            <div className="flex items-center space-x-2">
                                                <span className="font-medium text-gray-900">${product.price}</span>
                                                {product.originalPrice > product.price && (
                                                    <span className="text-sm text-gray-500 line-through">
                                                        ${product.originalPrice}
                                                    </span>
                                                )}
                                            </div>
                                            <span className="text-sm text-gray-500">
                                                {Math.round(product.similarity * 100)}% match
                                            </span>
                                        </div>

                                        <div className="flex items-center justify-between">
                                            <span className={`text-sm ${product.inStock ? 'text-green-600' : 'text-red-600'}`}>
                                                {product.inStock ? 'In Stock' : 'Out of Stock'}
                                            </span>
                                            <div className="flex items-center space-x-2">
                                                <button className="p-2 text-gray-400 hover:text-gray-600">
                                                    <Heart className="h-4 w-4" />
                                                </button>
                                                <button className="p-2 text-gray-400 hover:text-gray-600">
                                                    <Eye className="h-4 w-4" />
                                                </button>
                                                <button className="p-2 text-gray-400 hover:text-gray-600">
                                                    <ShoppingCart className="h-4 w-4" />
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}
