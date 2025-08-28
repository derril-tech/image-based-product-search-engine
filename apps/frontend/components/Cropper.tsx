'use client'

import { useState, useRef, useCallback, useEffect } from 'react'
import { Crop, RotateCcw, ZoomIn, ZoomOut, Check, X } from 'lucide-react'

interface CropArea {
    x: number
    y: number
    width: number
    height: number
}

interface CropperProps {
    imageUrl: string
    onCrop: (croppedImage: Blob, cropArea: CropArea) => void
    onCancel: () => void
    aspectRatio?: number
    className?: string
    showControls?: boolean
}

export default function Cropper({
    imageUrl,
    onCrop,
    onCancel,
    aspectRatio,
    className = '',
    showControls = true
}: CropperProps) {
    const [cropArea, setCropArea] = useState<CropArea>({ x: 0, y: 0, width: 100, height: 100 })
    const [isDragging, setIsDragging] = useState(false)
    const [dragStart, setDragStart] = useState({ x: 0, y: 0 })
    const [scale, setScale] = useState(1)
    const [rotation, setRotation] = useState(0)
    const containerRef = useRef<HTMLDivElement>(null)
    const imageRef = useRef<HTMLImageElement>(null)

    const handleMouseDown = useCallback((e: React.MouseEvent) => {
        if (!containerRef.current) return

        const rect = containerRef.current.getBoundingClientRect()
        const x = ((e.clientX - rect.left) / rect.width) * 100
        const y = ((e.clientY - rect.top) / rect.height) * 100

        setIsDragging(true)
        setDragStart({ x, y })
    }, [])

    const handleMouseMove = useCallback((e: React.MouseEvent) => {
        if (!isDragging || !containerRef.current) return

        const rect = containerRef.current.getBoundingClientRect()
        const x = ((e.clientX - rect.left) / rect.width) * 100
        const y = ((e.clientY - rect.top) / rect.height) * 100

        const deltaX = x - dragStart.x
        const deltaY = y - dragStart.y

        setCropArea(prev => ({
            x: Math.max(0, Math.min(100 - prev.width, prev.x + deltaX)),
            y: Math.max(0, Math.min(100 - prev.height, prev.y + deltaY)),
            width: prev.width,
            height: prev.height
        }))

        setDragStart({ x, y })
    }, [isDragging, dragStart])

    const handleMouseUp = useCallback(() => {
        setIsDragging(false)
    }, [])

    const handleResize = useCallback((direction: string, e: React.MouseEvent) => {
        if (!containerRef.current) return

        const rect = containerRef.current.getBoundingClientRect()
        const x = ((e.clientX - rect.left) / rect.width) * 100
        const y = ((e.clientY - rect.top) / rect.height) * 100

        setCropArea(prev => {
            let newCrop = { ...prev }

            switch (direction) {
                case 'nw':
                    newCrop.x = Math.min(x, prev.x + prev.width - 10)
                    newCrop.y = Math.min(y, prev.y + prev.height - 10)
                    newCrop.width = Math.max(10, prev.x + prev.width - newCrop.x)
                    newCrop.height = Math.max(10, prev.y + prev.height - newCrop.y)
                    break
                case 'ne':
                    newCrop.y = Math.min(y, prev.y + prev.height - 10)
                    newCrop.width = Math.max(10, x - newCrop.x)
                    newCrop.height = Math.max(10, prev.y + prev.height - newCrop.y)
                    break
                case 'sw':
                    newCrop.x = Math.min(x, prev.x + prev.width - 10)
                    newCrop.width = Math.max(10, prev.x + prev.width - newCrop.x)
                    newCrop.height = Math.max(10, y - newCrop.y)
                    break
                case 'se':
                    newCrop.width = Math.max(10, x - newCrop.x)
                    newCrop.height = Math.max(10, y - newCrop.y)
                    break
            }

            // Maintain aspect ratio if specified
            if (aspectRatio) {
                if (direction.includes('e') || direction.includes('w')) {
                    newCrop.height = newCrop.width / aspectRatio
                } else {
                    newCrop.width = newCrop.height * aspectRatio
                }
            }

            return newCrop
        })
    }, [aspectRatio])

    const handleAutoCrop = useCallback(() => {
        // Simple auto-crop that centers the crop area
        setCropArea({
            x: 10,
            y: 10,
            width: 80,
            height: aspectRatio ? 80 / aspectRatio : 80
        })
    }, [aspectRatio])

    const handleCrop = useCallback(async () => {
        if (!imageRef.current) return

        const canvas = document.createElement('canvas')
        const ctx = canvas.getContext('2d')
        if (!ctx) return

        const img = imageRef.current
        const rect = containerRef.current?.getBoundingClientRect()
        if (!rect) return

        // Calculate actual crop dimensions
        const cropX = (cropArea.x / 100) * img.naturalWidth
        const cropY = (cropArea.y / 100) * img.naturalHeight
        const cropWidth = (cropArea.width / 100) * img.naturalWidth
        const cropHeight = (cropArea.height / 100) * img.naturalHeight

        canvas.width = cropWidth
        canvas.height = cropHeight

        // Apply transformations
        ctx.save()
        ctx.translate(canvas.width / 2, canvas.height / 2)
        ctx.rotate((rotation * Math.PI) / 180)
        ctx.scale(scale, scale)
        ctx.translate(-canvas.width / 2, -canvas.height / 2)

        ctx.drawImage(
            img,
            cropX, cropY, cropWidth, cropHeight,
            0, 0, cropWidth, cropHeight
        )

        ctx.restore()

        canvas.toBlob((blob) => {
            if (blob) {
                onCrop(blob, cropArea)
            }
        }, 'image/jpeg', 0.9)
    }, [cropArea, rotation, scale, onCrop])

    const handleZoomIn = () => setScale(prev => Math.min(prev + 0.1, 3))
    const handleZoomOut = () => setScale(prev => Math.max(prev - 0.1, 0.1))
    const handleRotate = () => setRotation(prev => (prev + 90) % 360)
    const handleReset = () => {
        setScale(1)
        setRotation(0)
        setCropArea({ x: 0, y: 0, width: 100, height: 100 })
    }

    useEffect(() => {
        const handleGlobalMouseUp = () => setIsDragging(false)
        document.addEventListener('mouseup', handleGlobalMouseUp)
        return () => document.removeEventListener('mouseup', handleGlobalMouseUp)
    }, [])

    return (
        <div className={`relative ${className}`}>
            <div
                ref={containerRef}
                className="relative bg-gray-100 rounded-lg overflow-hidden"
                onMouseDown={handleMouseDown}
                onMouseMove={handleMouseMove}
                onMouseUp={handleMouseUp}
            >
                <img
                    ref={imageRef}
                    src={imageUrl}
                    alt="Crop preview"
                    className="max-w-full h-auto"
                    style={{
                        transform: `scale(${scale}) rotate(${rotation}deg)`,
                        transformOrigin: 'center'
                    }}
                />

                {/* Crop overlay */}
                <div
                    className="absolute inset-0 pointer-events-none"
                    style={{
                        background: `linear-gradient(
                            to right,
                            rgba(0,0,0,0.5) 0%,
                            rgba(0,0,0,0.5) ${cropArea.x}%,
                            transparent ${cropArea.x}%,
                            transparent ${cropArea.x + cropArea.width}%,
                            rgba(0,0,0,0.5) ${cropArea.x + cropArea.width}%,
                            rgba(0,0,0,0.5) 100%
                        ),
                        linear-gradient(
                            to bottom,
                            rgba(0,0,0,0.5) 0%,
                            rgba(0,0,0,0.5) ${cropArea.y}%,
                            transparent ${cropArea.y}%,
                            transparent ${cropArea.y + cropArea.height}%,
                            rgba(0,0,0,0.5) ${cropArea.y + cropArea.height}%,
                            rgba(0,0,0,0.5) 100%
                        )`
                    }}
                />

                {/* Crop area */}
                <div
                    className="absolute border-2 border-blue-500 border-dashed pointer-events-none"
                    style={{
                        left: `${cropArea.x}%`,
                        top: `${cropArea.y}%`,
                        width: `${cropArea.width}%`,
                        height: `${cropArea.height}%`
                    }}
                />

                {/* Resize handles */}
                {['nw', 'ne', 'sw', 'se'].map((corner) => (
                    <div
                        key={corner}
                        className="absolute w-3 h-3 bg-blue-500 border-2 border-white rounded-full cursor-pointer"
                        style={{
                            left: corner.includes('w') ? `${cropArea.x - 1.5}%` : `${cropArea.x + cropArea.width - 1.5}%`,
                            top: corner.includes('n') ? `${cropArea.y - 1.5}%` : `${cropArea.y + cropArea.height - 1.5}%`
                        }}
                        onMouseDown={(e) => {
                            e.stopPropagation()
                            const handleResizeWithDirection = (e: MouseEvent) => {
                                handleResize(corner, e as any)
                            }
                            const handleMouseUp = () => {
                                document.removeEventListener('mousemove', handleResizeWithDirection)
                                document.removeEventListener('mouseup', handleMouseUp)
                            }
                            document.addEventListener('mousemove', handleResizeWithDirection)
                            document.addEventListener('mouseup', handleMouseUp)
                        }}
                    />
                ))}
            </div>

            {showControls && (
                <div className="mt-4 flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                        <button
                            onClick={handleAutoCrop}
                            className="px-3 py-1 border border-gray-300 rounded text-sm hover:bg-gray-50 flex items-center"
                        >
                            <Crop className="h-4 w-4 mr-1" />
                            Auto Crop
                        </button>
                        <button
                            onClick={handleZoomIn}
                            className="p-1 border border-gray-300 rounded hover:bg-gray-50"
                        >
                            <ZoomIn className="h-4 w-4" />
                        </button>
                        <button
                            onClick={handleZoomOut}
                            className="p-1 border border-gray-300 rounded hover:bg-gray-50"
                        >
                            <ZoomOut className="h-4 w-4" />
                        </button>
                        <button
                            onClick={handleRotate}
                            className="p-1 border border-gray-300 rounded hover:bg-gray-50"
                        >
                            <RotateCcw className="h-4 w-4" />
                        </button>
                        <button
                            onClick={handleReset}
                            className="px-3 py-1 border border-gray-300 rounded text-sm hover:bg-gray-50"
                        >
                            Reset
                        </button>
                    </div>
                    <div className="flex items-center space-x-2">
                        <button
                            onClick={onCancel}
                            className="px-4 py-2 text-gray-600 hover:text-gray-700 flex items-center"
                        >
                            <X className="h-4 w-4 mr-1" />
                            Cancel
                        </button>
                        <button
                            onClick={handleCrop}
                            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center"
                        >
                            <Check className="h-4 w-4 mr-1" />
                            Crop
                        </button>
                    </div>
                </div>
            )}
        </div>
    )
}
