'use client'

import { useState } from 'react'
import { Search, Filter, MoreHorizontal, Edit, Trash2, Eye, Download, ChevronDown, ChevronUp } from 'lucide-react'

interface CatalogItem {
    id: number
    name: string
    sku: string
    category: string
    brand: string
    price: number
    stock: number
    status: 'active' | 'inactive' | 'draft'
    lastUpdated: string
    image?: string
}

interface CatalogTableProps {
    items: CatalogItem[]
    onItemClick?: (item: CatalogItem) => void
    onEditItem?: (item: CatalogItem) => void
    onDeleteItem?: (item: CatalogItem) => void
    onExport?: () => void
    className?: string
    searchable?: boolean
    filterable?: boolean
    sortable?: boolean
    selectable?: boolean
}

type SortField = 'name' | 'sku' | 'category' | 'brand' | 'price' | 'stock' | 'status' | 'lastUpdated'
type SortDirection = 'asc' | 'desc'

export default function CatalogTable({
    items,
    onItemClick,
    onEditItem,
    onDeleteItem,
    onExport,
    className = '',
    searchable = true,
    filterable = true,
    sortable = true,
    selectable = true
}: CatalogTableProps) {
    const [searchQuery, setSearchQuery] = useState('')
    const [selectedItems, setSelectedItems] = useState<Set<number>>(new Set())
    const [sortField, setSortField] = useState<SortField>('name')
    const [sortDirection, setSortDirection] = useState<SortDirection>('asc')
    const [statusFilter, setStatusFilter] = useState<string>('all')
    const [categoryFilter, setCategoryFilter] = useState<string>('all')

    // Get unique categories and brands for filters
    const categories = Array.from(new Set(items.map(item => item.category)))
    const brands = Array.from(new Set(items.map(item => item.brand)))

    const handleSort = (field: SortField) => {
        if (sortField === field) {
            setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')
        } else {
            setSortField(field)
            setSortDirection('asc')
        }
    }

    const handleSelectAll = () => {
        if (selectedItems.size === filteredItems.length) {
            setSelectedItems(new Set())
        } else {
            setSelectedItems(new Set(filteredItems.map(item => item.id)))
        }
    }

    const handleSelectItem = (itemId: number) => {
        const newSelected = new Set(selectedItems)
        if (newSelected.has(itemId)) {
            newSelected.delete(itemId)
        } else {
            newSelected.add(itemId)
        }
        setSelectedItems(newSelected)
    }

    const getSortIcon = (field: SortField) => {
        if (sortField !== field) {
            return <ChevronDown className="h-4 w-4 text-gray-400" />
        }
        return sortDirection === 'asc' ?
            <ChevronUp className="h-4 w-4 text-blue-600" /> :
            <ChevronDown className="h-4 w-4 text-blue-600" />
    }

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'active':
                return 'bg-green-100 text-green-800'
            case 'inactive':
                return 'bg-red-100 text-red-800'
            case 'draft':
                return 'bg-yellow-100 text-yellow-800'
            default:
                return 'bg-gray-100 text-gray-800'
        }
    }

    // Filter and sort items
    const filteredItems = items
        .filter(item => {
            const matchesSearch = searchQuery === '' ||
                item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                item.sku.toLowerCase().includes(searchQuery.toLowerCase()) ||
                item.brand.toLowerCase().includes(searchQuery.toLowerCase())

            const matchesStatus = statusFilter === 'all' || item.status === statusFilter
            const matchesCategory = categoryFilter === 'all' || item.category === categoryFilter

            return matchesSearch && matchesStatus && matchesCategory
        })
        .sort((a, b) => {
            let aValue = a[sortField]
            let bValue = b[sortField]

            if (typeof aValue === 'string') {
                aValue = aValue.toLowerCase()
                bValue = bValue.toLowerCase()
            }

            if (aValue < bValue) return sortDirection === 'asc' ? -1 : 1
            if (aValue > bValue) return sortDirection === 'asc' ? 1 : -1
            return 0
        })

    return (
        <div className={`bg-white rounded-lg shadow ${className}`}>
            {/* Header */}
            <div className="px-6 py-4 border-b border-gray-200">
                <div className="flex items-center justify-between">
                    <div>
                        <h3 className="text-lg font-medium text-gray-900">Catalog Items</h3>
                        <p className="text-sm text-gray-500">
                            {filteredItems.length} of {items.length} items
                        </p>
                    </div>
                    <div className="flex items-center space-x-2">
                        {onExport && (
                            <button
                                onClick={onExport}
                                className="px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 flex items-center"
                            >
                                <Download className="h-4 w-4 mr-2" />
                                Export
                            </button>
                        )}
                    </div>
                </div>

                {/* Search and Filters */}
                <div className="mt-4 flex items-center space-x-4">
                    {searchable && (
                        <div className="flex-1 max-w-md">
                            <div className="relative">
                                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                                <input
                                    type="text"
                                    placeholder="Search items..."
                                    value={searchQuery}
                                    onChange={(e) => setSearchQuery(e.target.value)}
                                    className="pl-10 pr-4 py-2 border border-gray-300 rounded-md w-full focus:outline-none focus:ring-2 focus:ring-blue-500"
                                />
                            </div>
                        </div>
                    )}

                    {filterable && (
                        <div className="flex items-center space-x-2">
                            <select
                                value={statusFilter}
                                onChange={(e) => setStatusFilter(e.target.value)}
                                className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                            >
                                <option value="all">All Status</option>
                                <option value="active">Active</option>
                                <option value="inactive">Inactive</option>
                                <option value="draft">Draft</option>
                            </select>

                            <select
                                value={categoryFilter}
                                onChange={(e) => setCategoryFilter(e.target.value)}
                                className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                            >
                                <option value="all">All Categories</option>
                                {categories.map(category => (
                                    <option key={category} value={category}>{category}</option>
                                ))}
                            </select>
                        </div>
                    )}
                </div>
            </div>

            {/* Table */}
            <div className="overflow-x-auto">
                <table className="w-full">
                    <thead className="bg-gray-50">
                        <tr>
                            {selectable && (
                                <th className="px-6 py-3 text-left">
                                    <input
                                        type="checkbox"
                                        checked={selectedItems.size === filteredItems.length && filteredItems.length > 0}
                                        onChange={handleSelectAll}
                                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                                    />
                                </th>
                            )}
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Item
                            </th>
                            {sortable ? (
                                <>
                                    <th
                                        className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                                        onClick={() => handleSort('sku')}
                                    >
                                        <div className="flex items-center space-x-1">
                                            <span>SKU</span>
                                            {getSortIcon('sku')}
                                        </div>
                                    </th>
                                    <th
                                        className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                                        onClick={() => handleSort('category')}
                                    >
                                        <div className="flex items-center space-x-1">
                                            <span>Category</span>
                                            {getSortIcon('category')}
                                        </div>
                                    </th>
                                    <th
                                        className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                                        onClick={() => handleSort('brand')}
                                    >
                                        <div className="flex items-center space-x-1">
                                            <span>Brand</span>
                                            {getSortIcon('brand')}
                                        </div>
                                    </th>
                                    <th
                                        className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                                        onClick={() => handleSort('price')}
                                    >
                                        <div className="flex items-center space-x-1">
                                            <span>Price</span>
                                            {getSortIcon('price')}
                                        </div>
                                    </th>
                                    <th
                                        className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                                        onClick={() => handleSort('stock')}
                                    >
                                        <div className="flex items-center space-x-1">
                                            <span>Stock</span>
                                            {getSortIcon('stock')}
                                        </div>
                                    </th>
                                    <th
                                        className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                                        onClick={() => handleSort('status')}
                                    >
                                        <div className="flex items-center space-x-1">
                                            <span>Status</span>
                                            {getSortIcon('status')}
                                        </div>
                                    </th>
                                    <th
                                        className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                                        onClick={() => handleSort('lastUpdated')}
                                    >
                                        <div className="flex items-center space-x-1">
                                            <span>Last Updated</span>
                                            {getSortIcon('lastUpdated')}
                                        </div>
                                    </th>
                                </>
                            ) : (
                                <>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">SKU</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Category</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Brand</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Price</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Stock</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Last Updated</th>
                                </>
                            )}
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Actions
                            </th>
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                        {filteredItems.map((item) => (
                            <tr
                                key={item.id}
                                className="hover:bg-gray-50 cursor-pointer"
                                onClick={() => onItemClick?.(item)}
                            >
                                {selectable && (
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <input
                                            type="checkbox"
                                            checked={selectedItems.has(item.id)}
                                            onChange={() => handleSelectItem(item.id)}
                                            onClick={(e) => e.stopPropagation()}
                                            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                                        />
                                    </td>
                                )}
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <div className="flex items-center">
                                        {item.image && (
                                            <img
                                                src={item.image}
                                                alt={item.name}
                                                className="h-10 w-10 rounded-lg object-cover mr-3"
                                            />
                                        )}
                                        <div>
                                            <div className="text-sm font-medium text-gray-900">{item.name}</div>
                                        </div>
                                    </div>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{item.sku}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{item.category}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{item.brand}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${item.price}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{item.stock}</td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(item.status)}`}>
                                        {item.status}
                                    </span>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                    {new Date(item.lastUpdated).toLocaleDateString()}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                    <div className="flex items-center space-x-2">
                                        <button
                                            onClick={(e) => {
                                                e.stopPropagation()
                                                onItemClick?.(item)
                                            }}
                                            className="text-gray-400 hover:text-gray-600"
                                        >
                                            <Eye className="h-4 w-4" />
                                        </button>
                                        <button
                                            onClick={(e) => {
                                                e.stopPropagation()
                                                onEditItem?.(item)
                                            }}
                                            className="text-gray-400 hover:text-gray-600"
                                        >
                                            <Edit className="h-4 w-4" />
                                        </button>
                                        <button
                                            onClick={(e) => {
                                                e.stopPropagation()
                                                onDeleteItem?.(item)
                                            }}
                                            className="text-gray-400 hover:text-red-600"
                                        >
                                            <Trash2 className="h-4 w-4" />
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {/* Empty State */}
            {filteredItems.length === 0 && (
                <div className="text-center py-12">
                    <div className="bg-gray-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                        <Search className="h-8 w-8 text-gray-400" />
                    </div>
                    <h3 className="text-lg font-medium text-gray-900 mb-2">No items found</h3>
                    <p className="text-gray-600">Try adjusting your search criteria or filters.</p>
                </div>
            )}
        </div>
    )
}
