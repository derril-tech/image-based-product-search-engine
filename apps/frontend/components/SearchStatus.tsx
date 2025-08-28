'use client'

import { useState, useEffect } from 'react'
import { Activity, CheckCircle, XCircle, Clock, Wifi, WifiOff } from 'lucide-react'
import { useSearchWebSocket, SearchStatus, formatSearchStatus, getStatusColor } from '../lib/websocket'

export interface SearchStatusProps {
    searchId?: string
    websocketUrl: string
    onComplete?: (results: any[]) => void
    onError?: (error: string) => void
    className?: string
    showConnectionStatus?: boolean
    autoSubscribe?: boolean
}

export default function SearchStatus({
    searchId,
    websocketUrl,
    onComplete,
    onError,
    className = '',
    showConnectionStatus = true,
    autoSubscribe = true
}: SearchStatusProps) {
    const [currentStatus, setCurrentStatus] = useState<SearchStatus | null>(null)
    const [isVisible, setIsVisible] = useState(false)

    const {
        isConnected,
        lastStatus,
        error: wsError,
        subscribeToSearch,
        unsubscribeFromSearch
    } = useSearchWebSocket(websocketUrl, {
        autoReconnect: true,
        heartbeatInterval: 30000,
        onStatusUpdate: (status) => {
            setCurrentStatus(status)
            setIsVisible(true)

            if (status.status === 'completed' && status.results) {
                onComplete?.(status.results)
            } else if (status.status === 'failed') {
                onError?.(status.error || 'Search failed')
            }
        },
        onError: (error) => {
            onError?.(error)
        }
    })

    useEffect(() => {
        if (searchId && autoSubscribe && isConnected) {
            subscribeToSearch(searchId)
            return () => unsubscribeFromSearch(searchId)
        }
    }, [searchId, autoSubscribe, isConnected, subscribeToSearch, unsubscribeFromSearch])

    useEffect(() => {
        if (lastStatus) {
            setCurrentStatus(lastStatus)
            setIsVisible(true)
        }
    }, [lastStatus])

    const getStatusIcon = (status: SearchStatus) => {
        switch (status.status) {
            case 'pending':
                return <Clock className="h-5 w-5 text-yellow-500" />
            case 'processing':
                return <Activity className="h-5 w-5 text-blue-500 animate-pulse" />
            case 'completed':
                return <CheckCircle className="h-5 w-5 text-green-500" />
            case 'failed':
                return <XCircle className="h-5 w-5 text-red-500" />
            default:
                return <Activity className="h-5 w-5 text-gray-500" />
        }
    }

    const getProgressBarColor = (status: SearchStatus) => {
        switch (status.status) {
            case 'pending':
                return 'bg-yellow-500'
            case 'processing':
                return 'bg-blue-500'
            case 'completed':
                return 'bg-green-500'
            case 'failed':
                return 'bg-red-500'
            default:
                return 'bg-gray-500'
        }
    }

    if (!isVisible && !showConnectionStatus) {
        return null
    }

    return (
        <div className={`bg-white rounded-lg shadow p-4 space-y-4 ${className}`}>
            {/* Connection Status */}
            {showConnectionStatus && (
                <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                        {isConnected ? (
                            <Wifi className="h-4 w-4 text-green-500" />
                        ) : (
                            <WifiOff className="h-4 w-4 text-red-500" />
                        )}
                        <span className="text-sm text-gray-600">
                            {isConnected ? 'Connected' : 'Disconnected'}
                        </span>
                    </div>
                    {wsError && (
                        <span className="text-sm text-red-600">{wsError}</span>
                    )}
                </div>
            )}

            {/* Search Status */}
            {currentStatus && (
                <div className="space-y-3">
                    <div className="flex items-center space-x-3">
                        {getStatusIcon(currentStatus)}
                        <div className="flex-1">
                            <h3 className="font-medium text-gray-900">
                                {formatSearchStatus(currentStatus)}
                            </h3>
                            <p className="text-sm text-gray-600">{currentStatus.message}</p>
                        </div>
                        <span className={`text-sm font-medium ${getStatusColor(currentStatus)}`}>
                            {currentStatus.status}
                        </span>
                    </div>

                    {/* Progress Bar */}
                    {(currentStatus.status === 'pending' || currentStatus.status === 'processing') && (
                        <div className="space-y-2">
                            <div className="flex justify-between text-sm text-gray-600">
                                <span>Progress</span>
                                <span>{Math.round(currentStatus.progress)}%</span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-2">
                                <div
                                    className={`h-2 rounded-full transition-all duration-300 ${getProgressBarColor(currentStatus)}`}
                                    style={{ width: `${currentStatus.progress}%` }}
                                />
                            </div>
                        </div>
                    )}

                    {/* Error Message */}
                    {currentStatus.status === 'failed' && currentStatus.error && (
                        <div className="p-3 bg-red-50 border border-red-200 rounded-md">
                            <p className="text-sm text-red-600">{currentStatus.error}</p>
                        </div>
                    )}

                    {/* Results Preview */}
                    {currentStatus.status === 'completed' && currentStatus.results && (
                        <div className="p-3 bg-green-50 border border-green-200 rounded-md">
                            <p className="text-sm text-green-700">
                                Found {currentStatus.results.length} result{currentStatus.results.length !== 1 ? 's' : ''}
                            </p>
                        </div>
                    )}

                    {/* Timestamp */}
                    <div className="text-xs text-gray-500">
                        {new Date(currentStatus.timestamp).toLocaleTimeString()}
                    </div>
                </div>
            )}

            {/* No Status */}
            {!currentStatus && isConnected && (
                <div className="text-center py-4">
                    <Activity className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                    <p className="text-sm text-gray-600">Waiting for search status...</p>
                </div>
            )}

            {/* Not Connected */}
            {!isConnected && (
                <div className="text-center py-4">
                    <WifiOff className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                    <p className="text-sm text-gray-600">Not connected to search service</p>
                </div>
            )}
        </div>
    )
}
