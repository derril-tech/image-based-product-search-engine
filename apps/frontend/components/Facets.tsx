'use client'

import { useState } from 'react'
import { Filter, ChevronDown, ChevronUp, X } from 'lucide-react'

interface FacetOption {
    name: string
    count: number
    selected: boolean
}

interface FacetsData {
    [key: string]: FacetOption[]
}

interface FacetsProps {
    facets: FacetsData
    selectedFacets: { [key: string]: string[] }
    onFacetChange: (facetType: string, value: string) => void
    onClearAll: () => void
    className?: string
    collapsible?: boolean
    showCounts?: boolean
    maxVisible?: number
}

export default function Facets({
    facets,
    selectedFacets,
    onFacetChange,
    onClearAll,
    className = '',
    collapsible = true,
    showCounts = true,
    maxVisible = 5
}: FacetsProps) {
    const [expandedFacets, setExpandedFacets] = useState<Set<string>>(new Set())
    const [expandedOptions, setExpandedOptions] = useState<Set<string>>(new Set())

    const toggleFacet = (facetType: string) => {
        const newExpanded = new Set(expandedFacets)
        if (newExpanded.has(facetType)) {
            newExpanded.delete(facetType)
        } else {
            newExpanded.add(facetType)
        }
        setExpandedFacets(newExpanded)
    }

    const toggleOptions = (facetType: string) => {
        const newExpanded = new Set(expandedOptions)
        if (newExpanded.has(facetType)) {
            newExpanded.delete(facetType)
        } else {
            newExpanded.add(facetType)
        }
        setExpandedOptions(newExpanded)
    }

    const getActiveFiltersCount = () => {
        return Object.values(selectedFacets).flat().length
    }

    const handleFacetChange = (facetType: string, value: string) => {
        onFacetChange(facetType, value)
    }

    const clearFacet = (facetType: string) => {
        const current = selectedFacets[facetType] || []
        current.forEach(value => {
            onFacetChange(facetType, value)
        })
    }

    const getVisibleOptions = (options: FacetOption[], facetType: string) => {
        const isExpanded = expandedOptions.has(facetType)
        return isExpanded ? options : options.slice(0, maxVisible)
    }

    const hasMoreOptions = (options: FacetOption[], facetType: string) => {
        return options.length > maxVisible && !expandedOptions.has(facetType)
    }

    return (
        <div className={`bg-white rounded-lg shadow p-4 space-y-6 ${className}`}>
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                    <Filter className="h-5 w-5 text-gray-600" />
                    <h3 className="font-medium text-gray-900">Filters</h3>
                    {getActiveFiltersCount() > 0 && (
                        <span className="bg-blue-600 text-white text-xs rounded-full px-2 py-1">
                            {getActiveFiltersCount()}
                        </span>
                    )}
                </div>
                {getActiveFiltersCount() > 0 && (
                    <button
                        onClick={onClearAll}
                        className="text-sm text-blue-600 hover:text-blue-700"
                    >
                        Clear all
                    </button>
                )}
            </div>

            {/* Active Filters */}
            {getActiveFiltersCount() > 0 && (
                <div className="space-y-2">
                    <h4 className="text-sm font-medium text-gray-700">Active Filters</h4>
                    <div className="flex flex-wrap gap-2">
                        {Object.entries(selectedFacets).map(([facetType, values]) =>
                            values.map((value) => (
                                <span
                                    key={`${facetType}-${value}`}
                                    className="inline-flex items-center px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full"
                                >
                                    {value}
                                    <button
                                        onClick={() => handleFacetChange(facetType, value)}
                                        className="ml-1 hover:text-blue-900"
                                    >
                                        <X className="h-3 w-3" />
                                    </button>
                                </span>
                            ))
                        )}
                    </div>
                </div>
            )}

            {/* Facet Groups */}
            <div className="space-y-4">
                {Object.entries(facets).map(([facetType, options]) => {
                    const isExpanded = expandedFacets.has(facetType)
                    const visibleOptions = getVisibleOptions(options, facetType)
                    const hasMore = hasMoreOptions(options, facetType)
                    const selectedCount = selectedFacets[facetType]?.length || 0

                    return (
                        <div key={facetType} className="border-b border-gray-200 pb-4 last:border-b-0">
                            <div className="flex items-center justify-between mb-3">
                                <button
                                    onClick={() => collapsible ? toggleFacet(facetType) : undefined}
                                    className={`flex items-center space-x-2 ${collapsible ? 'cursor-pointer hover:text-gray-700' : ''
                                        }`}
                                >
                                    <span className="font-medium text-gray-900 capitalize">
                                        {facetType}
                                    </span>
                                    {selectedCount > 0 && (
                                        <span className="bg-blue-100 text-blue-800 text-xs rounded-full px-2 py-1">
                                            {selectedCount}
                                        </span>
                                    )}
                                    {collapsible && (
                                        isExpanded ? (
                                            <ChevronUp className="h-4 w-4 text-gray-500" />
                                        ) : (
                                            <ChevronDown className="h-4 w-4 text-gray-500" />
                                        )
                                    )}
                                </button>
                                {selectedCount > 0 && (
                                    <button
                                        onClick={() => clearFacet(facetType)}
                                        className="text-xs text-gray-500 hover:text-gray-700"
                                    >
                                        Clear
                                    </button>
                                )}
                            </div>

                            {(!collapsible || isExpanded) && (
                                <div className="space-y-2">
                                    {visibleOptions.map((option) => (
                                        <label
                                            key={option.name}
                                            className="flex items-center space-x-2 cursor-pointer hover:bg-gray-50 p-1 rounded"
                                        >
                                            <input
                                                type="checkbox"
                                                checked={selectedFacets[facetType]?.includes(option.name) || false}
                                                onChange={() => handleFacetChange(facetType, option.name)}
                                                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                                            />
                                            <span className="flex-1 text-sm text-gray-700">
                                                {option.name}
                                            </span>
                                            {showCounts && (
                                                <span className="text-xs text-gray-500">
                                                    ({option.count})
                                                </span>
                                            )}
                                        </label>
                                    ))}

                                    {hasMore && (
                                        <button
                                            onClick={() => toggleOptions(facetType)}
                                            className="text-sm text-blue-600 hover:text-blue-700 w-full text-left"
                                        >
                                            Show {options.length - maxVisible} more
                                        </button>
                                    )}

                                    {expandedOptions.has(facetType) && options.length > maxVisible && (
                                        <button
                                            onClick={() => toggleOptions(facetType)}
                                            className="text-sm text-blue-600 hover:text-blue-700 w-full text-left"
                                        >
                                            Show less
                                        </button>
                                    )}
                                </div>
                            )}
                        </div>
                    )
                })}
            </div>

            {/* No Facets State */}
            {Object.keys(facets).length === 0 && (
                <div className="text-center py-4">
                    <p className="text-sm text-gray-500">No filters available</p>
                </div>
            )}
        </div>
    )
}
