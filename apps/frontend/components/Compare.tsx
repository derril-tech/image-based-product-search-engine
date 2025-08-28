'use client'

import { useState } from 'react'
import { X, Star, ShoppingCart, Heart, Eye, ArrowLeft, ArrowRight } from 'lucide-react'

interface Product {
    id: number
    name: string
    price: number
    originalPrice?: number
    image: string
    brand: string
    rating: number
    reviews: number
    description?: string
    inStock: boolean
    category?: string
    features?: string[]
    specifications?: { [key: string]: string }
}

interface CompareProps {
    products: Product[]
    onRemoveProduct: (productId: number) => void
    onAddToCart?: (product: Product) => void
    onAddToWishlist?: (product: Product) => void
    onViewProduct?: (product: Product) => void
    maxProducts?: number
    className?: string
}

export default function Compare({
    products,
    onRemoveProduct,
    onAddToCart,
    onAddToWishlist,
    onViewProduct,
    maxProducts = 4,
    className = ''
}: CompareProps) {
    const [wishlistItems, setWishlistItems] = useState<Set<number>>(new Set())
    const [currentPage, setCurrentPage] = useState(0)

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

    const handleViewProduct = (product: Product) => {
        onViewProduct?.(product)
    }

    const totalPages = Math.ceil(products.length / maxProducts)
    const startIndex = currentPage * maxProducts
    const visibleProducts = products.slice(startIndex, startIndex + maxProducts)

    const getCommonFeatures = () => {
        if (visibleProducts.length === 0) return []

        const allFeatures = visibleProducts
            .map(p => p.features || [])
            .filter(features => features.length > 0)

        if (allFeatures.length === 0) return []

        const featureSets = allFeatures.map(features => new Set(features))
        const commonFeatures = featureSets.reduce((common, current) => {
            return new Set([...common].filter(feature => current.has(feature)))
        })

        return Array.from(commonFeatures)
    }

    const getCommonSpecifications = () => {
        if (visibleProducts.length === 0) return []

        const allSpecs = visibleProducts
            .map(p => p.specifications || {})
            .filter(specs => Object.keys(specs).length > 0)

        if (allSpecs.length === 0) return []

        const specKeys = allSpecs.map(specs => Object.keys(specs))
        const commonKeys = specKeys.reduce((common, current) => {
            return common.filter(key => current.includes(key))
        })

        return commonKeys
    }

    const commonFeatures = getCommonFeatures()
    const commonSpecs = getCommonSpecifications()

    if (products.length === 0) {
        return (
            <div className={`text-center py-12 ${className}`}>
                <div className="bg-gray-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                    <Eye className="h-8 w-8 text-gray-400" />
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">No products to compare</h3>
                <p className="text-gray-600">Add products to your comparison to see them side by side.</p>
            </div>
        )
    }

    return (
        <div className={`space-y-6 ${className}`}>
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-xl font-bold text-gray-900">Compare Products</h2>
                    <p className="text-gray-600">
                        {products.length} product{products.length !== 1 ? 's' : ''} selected
                    </p>
                </div>
                {totalPages > 1 && (
                    <div className="flex items-center space-x-2">
                        <button
                            onClick={() => setCurrentPage(prev => Math.max(0, prev - 1))}
                            disabled={currentPage === 0}
                            className="p-2 border border-gray-300 rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            <ArrowLeft className="h-4 w-4" />
                        </button>
                        <span className="text-sm text-gray-600">
                            {currentPage + 1} of {totalPages}
                        </span>
                        <button
                            onClick={() => setCurrentPage(prev => Math.min(totalPages - 1, prev + 1))}
                            disabled={currentPage === totalPages - 1}
                            className="p-2 border border-gray-300 rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            <ArrowRight className="h-4 w-4" />
                        </button>
                    </div>
                )}
            </div>

            {/* Products Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {visibleProducts.map((product) => (
                    <div key={product.id} className="bg-white rounded-lg shadow p-4 relative">
                        {/* Remove Button */}
                        <button
                            onClick={() => onRemoveProduct(product.id)}
                            className="absolute top-2 right-2 p-1 bg-red-500 text-white rounded-full hover:bg-red-600 transition-colors"
                        >
                            <X className="h-4 w-4" />
                        </button>

                        {/* Product Image */}
                        <div className="mb-4">
                            <img
                                src={product.image}
                                alt={product.name}
                                className="w-full h-48 object-cover rounded-lg"
                            />
                        </div>

                        {/* Product Info */}
                        <div className="space-y-3">
                            <h3 className="font-medium text-gray-900 line-clamp-2">{product.name}</h3>
                            <p className="text-sm text-gray-500">{product.brand}</p>

                            {/* Rating */}
                            <div className="flex items-center space-x-1">
                                <Star className="h-4 w-4 text-yellow-400 fill-current" />
                                <span className="text-sm text-gray-600">{product.rating}</span>
                                <span className="text-sm text-gray-500">({product.reviews})</span>
                            </div>

                            {/* Price */}
                            <div className="flex items-center space-x-2">
                                <span className="font-medium text-gray-900">${product.price}</span>
                                {product.originalPrice && product.originalPrice > product.price && (
                                    <span className="text-sm text-gray-500 line-through">
                                        ${product.originalPrice}
                                    </span>
                                )}
                            </div>

                            {/* Stock Status */}
                            <span className={`text-sm ${product.inStock ? 'text-green-600' : 'text-red-600'}`}>
                                {product.inStock ? 'In Stock' : 'Out of Stock'}
                            </span>

                            {/* Actions */}
                            <div className="flex items-center space-x-2 pt-2">
                                <button
                                    onClick={() => handleViewProduct(product)}
                                    className="flex-1 bg-blue-600 text-white px-3 py-2 rounded-md text-sm hover:bg-blue-700 transition-colors"
                                >
                                    View
                                </button>
                                <button
                                    onClick={() => handleWishlistToggle(product)}
                                    className={`p-2 rounded-md transition-colors ${wishlistItems.has(product.id)
                                            ? 'text-red-500 bg-red-50'
                                            : 'text-gray-400 hover:text-gray-600'
                                        }`}
                                >
                                    <Heart className={`h-4 w-4 ${wishlistItems.has(product.id) ? 'fill-current' : ''}`} />
                                </button>
                                <button
                                    onClick={() => handleAddToCart(product)}
                                    disabled={!product.inStock}
                                    className={`p-2 rounded-md transition-colors ${product.inStock
                                            ? 'text-gray-400 hover:text-gray-600'
                                            : 'text-gray-300 cursor-not-allowed'
                                        }`}
                                >
                                    <ShoppingCart className="h-4 w-4" />
                                </button>
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            {/* Comparison Table */}
            {visibleProducts.length > 1 && (
                <div className="bg-white rounded-lg shadow overflow-hidden">
                    <div className="px-6 py-4 border-b border-gray-200">
                        <h3 className="text-lg font-medium text-gray-900">Detailed Comparison</h3>
                    </div>

                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <tbody>
                                {/* Basic Info */}
                                <tr className="border-b border-gray-200">
                                    <td className="px-6 py-4 bg-gray-50 font-medium text-gray-900">Product</td>
                                    {visibleProducts.map((product) => (
                                        <td key={product.id} className="px-6 py-4">
                                            <div className="text-center">
                                                <img
                                                    src={product.image}
                                                    alt={product.name}
                                                    className="w-16 h-16 object-cover rounded mx-auto mb-2"
                                                />
                                                <p className="font-medium text-gray-900">{product.name}</p>
                                                <p className="text-sm text-gray-500">{product.brand}</p>
                                            </div>
                                        </td>
                                    ))}
                                </tr>

                                <tr className="border-b border-gray-200">
                                    <td className="px-6 py-4 bg-gray-50 font-medium text-gray-900">Price</td>
                                    {visibleProducts.map((product) => (
                                        <td key={product.id} className="px-6 py-4 text-center">
                                            <span className="font-medium text-gray-900">${product.price}</span>
                                            {product.originalPrice && product.originalPrice > product.price && (
                                                <div className="text-sm text-gray-500 line-through">
                                                    ${product.originalPrice}
                                                </div>
                                            )}
                                        </td>
                                    ))}
                                </tr>

                                <tr className="border-b border-gray-200">
                                    <td className="px-6 py-4 bg-gray-50 font-medium text-gray-900">Rating</td>
                                    {visibleProducts.map((product) => (
                                        <td key={product.id} className="px-6 py-4 text-center">
                                            <div className="flex items-center justify-center space-x-1">
                                                <Star className="h-4 w-4 text-yellow-400 fill-current" />
                                                <span>{product.rating}</span>
                                            </div>
                                            <div className="text-sm text-gray-500">({product.reviews} reviews)</div>
                                        </td>
                                    ))}
                                </tr>

                                <tr className="border-b border-gray-200">
                                    <td className="px-6 py-4 bg-gray-50 font-medium text-gray-900">Availability</td>
                                    {visibleProducts.map((product) => (
                                        <td key={product.id} className="px-6 py-4 text-center">
                                            <span className={`text-sm ${product.inStock ? 'text-green-600' : 'text-red-600'}`}>
                                                {product.inStock ? 'In Stock' : 'Out of Stock'}
                                            </span>
                                        </td>
                                    ))}
                                </tr>

                                {/* Features */}
                                {commonFeatures.length > 0 && (
                                    <tr className="border-b border-gray-200">
                                        <td className="px-6 py-4 bg-gray-50 font-medium text-gray-900">Features</td>
                                        {visibleProducts.map((product) => (
                                            <td key={product.id} className="px-6 py-4">
                                                <ul className="space-y-1">
                                                    {commonFeatures.map((feature) => (
                                                        <li key={feature} className="text-sm text-gray-600">
                                                            {product.features?.includes(feature) ? '✓' : '✗'} {feature}
                                                        </li>
                                                    ))}
                                                </ul>
                                            </td>
                                        ))}
                                    </tr>
                                )}

                                {/* Specifications */}
                                {commonSpecs.length > 0 && commonSpecs.map((specKey) => (
                                    <tr key={specKey} className="border-b border-gray-200">
                                        <td className="px-6 py-4 bg-gray-50 font-medium text-gray-900 capitalize">
                                            {specKey.replace(/([A-Z])/g, ' $1').trim()}
                                        </td>
                                        {visibleProducts.map((product) => (
                                            <td key={product.id} className="px-6 py-4 text-center">
                                                <span className="text-sm text-gray-600">
                                                    {product.specifications?.[specKey] || 'N/A'}
                                                </span>
                                            </td>
                                        ))}
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
        </div>
    )
}
