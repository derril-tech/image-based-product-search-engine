'use client'

import { useState } from 'react'
import { Heart, Users, Lock, Globe, Edit, Trash2, Share2, Plus, Grid, List } from 'lucide-react'

interface Collection {
    id: number
    name: string
    description: string
    image: string
    productCount: number
    isPublic: boolean
    isShared: boolean
    sharedWith: string[]
    createdAt: string
    updatedAt: string
    tags: string[]
    coverColor: string
}

interface CollectionsProps {
    collections: Collection[]
    viewMode?: 'grid' | 'list'
    onViewModeChange?: (mode: 'grid' | 'list') => void
    onCollectionClick?: (collection: Collection) => void
    onEditCollection?: (collection: Collection) => void
    onDeleteCollection?: (collection: Collection) => void
    onShareCollection?: (collection: Collection) => void
    onCreateCollection?: () => void
    className?: string
    showActions?: boolean
    maxTags?: number
}

export default function Collections({
    collections,
    viewMode = 'grid',
    onViewModeChange,
    onCollectionClick,
    onEditCollection,
    onDeleteCollection,
    onShareCollection,
    onCreateCollection,
    className = '',
    showActions = true,
    maxTags = 2
}: CollectionsProps) {
    const [hoveredCollection, setHoveredCollection] = useState<number | null>(null)

    const handleCollectionClick = (collection: Collection) => {
        onCollectionClick?.(collection)
    }

    const handleEdit = (e: React.MouseEvent, collection: Collection) => {
        e.stopPropagation()
        onEditCollection?.(collection)
    }

    const handleDelete = (e: React.MouseEvent, collection: Collection) => {
        e.stopPropagation()
        onDeleteCollection?.(collection)
    }

    const handleShare = (e: React.MouseEvent, collection: Collection) => {
        e.stopPropagation()
        onShareCollection?.(collection)
    }

    return (
        <div className={className}>
            {/* Header with View Mode Toggle */}
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h2 className="text-xl font-bold text-gray-900">Collections</h2>
                    <p className="text-gray-600">{collections.length} collection{collections.length !== 1 ? 's' : ''}</p>
                </div>
                <div className="flex items-center space-x-4">
                    {onViewModeChange && (
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
                    )}
                    {onCreateCollection && (
                        <button
                            onClick={onCreateCollection}
                            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center"
                        >
                            <Plus className="h-4 w-4 mr-2" />
                            Create Collection
                        </button>
                    )}
                </div>
            </div>

            {/* Collections Grid/List */}
            <div className={`${viewMode === 'grid'
                    ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6'
                    : 'space-y-4'
                }`}>
                {collections.map((collection) => (
                    <div
                        key={collection.id}
                        className={`bg-white rounded-lg shadow hover:shadow-md transition-all cursor-pointer ${viewMode === 'list' ? 'flex space-x-4 p-4' : 'p-4'
                            }`}
                        onClick={() => handleCollectionClick(collection)}
                        onMouseEnter={() => setHoveredCollection(collection.id)}
                        onMouseLeave={() => setHoveredCollection(null)}
                    >
                        {/* Collection Image */}
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

                        {/* Collection Details */}
                        <div className="flex-1">
                            <div className="flex items-start justify-between mb-2">
                                <h3 className="font-medium text-gray-900">{collection.name}</h3>
                                {showActions && hoveredCollection === collection.id && (
                                    <div className="flex items-center space-x-1">
                                        <button
                                            onClick={(e) => handleShare(e, collection)}
                                            className="p-1 text-gray-400 hover:text-gray-600"
                                        >
                                            <Share2 className="h-4 w-4" />
                                        </button>
                                        <button
                                            onClick={(e) => handleEdit(e, collection)}
                                            className="p-1 text-gray-400 hover:text-gray-600"
                                        >
                                            <Edit className="h-4 w-4" />
                                        </button>
                                        <button
                                            onClick={(e) => handleDelete(e, collection)}
                                            className="p-1 text-gray-400 hover:text-red-600"
                                        >
                                            <Trash2 className="h-4 w-4" />
                                        </button>
                                    </div>
                                )}
                            </div>

                            <p className="text-sm text-gray-500 mb-3">{collection.description}</p>

                            <div className="flex items-center justify-between mb-3">
                                <span className="text-sm text-gray-600">
                                    {collection.productCount} products
                                </span>
                                <div className="flex items-center space-x-2">
                                    {collection.tags.slice(0, maxTags).map((tag) => (
                                        <span
                                            key={tag}
                                            className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full"
                                        >
                                            {tag}
                                        </span>
                                    ))}
                                    {collection.tags.length > maxTags && (
                                        <span className="text-xs text-gray-500">
                                            +{collection.tags.length - maxTags}
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

            {/* Empty State */}
            {collections.length === 0 && (
                <div className="text-center py-12">
                    <div className="bg-gray-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                        <Heart className="h-8 w-8 text-gray-400" />
                    </div>
                    <h3 className="text-lg font-medium text-gray-900 mb-2">No collections yet</h3>
                    <p className="text-gray-600 mb-4">Create your first collection to organize your favorite products.</p>
                    {onCreateCollection && (
                        <button
                            onClick={onCreateCollection}
                            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center mx-auto"
                        >
                            <Plus className="h-4 w-4 mr-2" />
                            Create Collection
                        </button>
                    )}
                </div>
            )}
        </div>
    )
}
