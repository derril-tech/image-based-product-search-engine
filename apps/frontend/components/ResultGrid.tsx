'use client'

import { useState } from 'react'
import { Heart, Eye, ShoppingCart, Star, Grid, List } from 'lucide-react'

interface Product {
    id: number
    name: string
    price: number
    originalPrice?: number
    image: string
    brand: string
    rating: number
    reviews: number
    similarity?: number
    inStock: boolean
    category?: string
}

interface ResultGridProps {
    products: Product[]
    viewMode?: 'grid' | 'list'
    onViewModeChange?: (mode: 'grid' | 'list') => void
    onProductClick?: (product: Product) => void
    onAddToWishlist?: (product: Product) => void
    onAddToCart?: (product: Product) => void
    className?: string
    showSimilarity?: boolean
    showActions?: boolean
}

export default function ResultGrid({
    products,
    viewMode = 'grid',
    onViewModeChange,
    onProductClick,
    onAddToWishlist,
    onAddToCart,
    className = '',
    showSimilarity = true,
    showActions = true
}: ResultGridProps) {
    const [wishlistItems, setWishlistItems] = useState<Set<number>>(new Set())

    const handleWishlistToggle = (product: Product) => {
        const newWishlist = new Set(wishlistItems)
        if (newWishlist.has(product.id)) {
            newWishlist.delete(product.id)
        } else {
            newWishlist.add(product.id)
        }
        setWishlistItems(newWishlist)
        onAddToWishlist?.(product)
    }

    const handleAddToCart = (product: Product) => {
        onAddToCart?.(product)
    }

    const handleProductClick = (product: Product) => {
        onProductClick?.(product)
    }

    return (
        <div className={className}>
            {/* View Mode Toggle */}
            {onViewModeChange && (
                <div className="flex justify-end mb-4">
                    <div className="flex border border-gray-300 rounded-md">
                        <button
                            onClick={() => onViewModeChange('grid')}
                            className={`p-2 ${viewMode === 'grid' ? 'bg-blue-600 text-white' : 'text-gray-600'}`}
                        >
                            <Grid className="h-4 w-4" />
                        </button>
                        <button
                            onClick={() => onViewModeChange('list')}
                            className={`p-2 ${viewMode === 'list' ? 'bg-blue-600 text-white' : 'text-gray-600'}`}
                        >
                            <List className="h-4 w-4" />
                        </button>
                    </div>
                </div>
            )}

            {/* Products Grid/List */}
            <div className={`${viewMode === 'grid'
                    ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6'
                    : 'space-y-4'
                }`}>
                {products.map((product) => (
                    <div
                        key={product.id}
                        className={`bg-white rounded-lg shadow hover:shadow-md transition-shadow cursor-pointer ${viewMode === 'list' ? 'flex space-x-4 p-4' : 'p-4'
                            }`}
                        onClick={() => handleProductClick(product)}
                    >
                        {/* Product Image */}
                        <div className={`${viewMode === 'list' ? 'w-32 flex-shrink-0' : 'mb-4'}`}>
                            <img
                                src={product.image}
                                alt={product.name}
                                className="w-full h-48 object-cover rounded-lg"
                            />
                        </div>

                        {/* Product Details */}
                        <div className="flex-1">
                            <div className="flex items-start justify-between mb-2">
                                <h3 className="font-medium text-gray-900 line-clamp-2">{product.name}</h3>
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
                                    {product.originalPrice && product.originalPrice > product.price && (
                                        <span className="text-sm text-gray-500 line-through">
                                            ${product.originalPrice}
                                        </span>
                                    )}
                                </div>
                                {showSimilarity && product.similarity && (
                                    <span className="text-sm text-gray-500">
                                        {Math.round(product.similarity * 100)}% match
                                    </span>
                                )}
                            </div>

                            <div className="flex items-center justify-between">
                                <span className={`text-sm ${product.inStock ? 'text-green-600' : 'text-red-600'}`}>
                                    {product.inStock ? 'In Stock' : 'Out of Stock'}
                                </span>

                                {showActions && (
                                    <div className="flex items-center space-x-2">
                                        <button
                                            onClick={(e) => {
                                                e.stopPropagation()
                                                handleWishlistToggle(product)
                                            }}
                                            className={`p-2 rounded-full transition-colors ${wishlistItems.has(product.id)
                                                    ? 'text-red-500 bg-red-50'
                                                    : 'text-gray-400 hover:text-gray-600'
                                                }`}
                                        >
                                            <Heart className={`h-4 w-4 ${wishlistItems.has(product.id) ? 'fill-current' : ''}`} />
                                        </button>
                                        <button
                                            onClick={(e) => {
                                                e.stopPropagation()
                                                handleProductClick(product)
                                            }}
                                            className="p-2 text-gray-400 hover:text-gray-600"
                                        >
                                            <Eye className="h-4 w-4" />
                                        </button>
                                        <button
                                            onClick={(e) => {
                                                e.stopPropagation()
                                                handleAddToCart(product)
                                            }}
                                            disabled={!product.inStock}
                                            className={`p-2 rounded-full transition-colors ${product.inStock
                                                    ? 'text-gray-400 hover:text-gray-600'
                                                    : 'text-gray-300 cursor-not-allowed'
                                                }`}
                                        >
                                            <ShoppingCart className="h-4 w-4" />
                                        </button>
                                    </div>
                                )}
                            </div>

                            {/* Category tag for list view */}
                            {viewMode === 'list' && product.category && (
                                <div className="mt-2">
                                    <span className="inline-block px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
                                        {product.category}
                                    </span>
                                </div>
                            )}
                        </div>
                    </div>
                ))}
            </div>

            {/* Empty State */}
            {products.length === 0 && (
                <div className="text-center py-12">
                    <div className="bg-gray-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                        <Eye className="h-8 w-8 text-gray-400" />
                    </div>
                    <h3 className="text-lg font-medium text-gray-900 mb-2">No products found</h3>
                    <p className="text-gray-600">Try adjusting your search criteria or filters.</p>
                </div>
            )}
        </div>
    )
}
