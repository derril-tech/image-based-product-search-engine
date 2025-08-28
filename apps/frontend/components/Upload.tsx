'use client'

import { useState, useRef, useCallback } from 'react'
import { Upload as UploadIcon, X, Image } from 'lucide-react'

interface UploadProps {
    onFileSelect: (file: File) => void
    onFileRemove?: () => void
    acceptedTypes?: string[]
    maxSize?: number // in MB
    className?: string
    disabled?: boolean
    placeholder?: string
    showPreview?: boolean
}

export default function Upload({
    onFileSelect,
    onFileRemove,
    acceptedTypes = ['image/*'],
    maxSize = 10, // 10MB default
    className = '',
    disabled = false,
    placeholder = 'Upload an image',
    showPreview = true
}: UploadProps) {
    const [isDragOver, setIsDragOver] = useState(false)
    const [selectedFile, setSelectedFile] = useState<File | null>(null)
    const [previewUrl, setPreviewUrl] = useState<string | null>(null)
    const [error, setError] = useState<string | null>(null)
    const fileInputRef = useRef<HTMLInputElement>(null)

    const validateFile = useCallback((file: File): string | null => {
        // Check file type
        const isValidType = acceptedTypes.some(type => {
            if (type === 'image/*') {
                return file.type.startsWith('image/')
            }
            return file.type === type
        })

        if (!isValidType) {
            return 'Invalid file type. Please upload an image.'
        }

        // Check file size
        if (file.size > maxSize * 1024 * 1024) {
            return `File size must be less than ${maxSize}MB.`
        }

        return null
    }, [acceptedTypes, maxSize])

    const handleFileSelect = useCallback((file: File) => {
        const validationError = validateFile(file)
        if (validationError) {
            setError(validationError)
            return
        }

        setError(null)
        setSelectedFile(file)
        onFileSelect(file)

        // Create preview URL
        if (showPreview) {
            const url = URL.createObjectURL(file)
            setPreviewUrl(url)
        }
    }, [validateFile, onFileSelect, showPreview])

    const handleFileInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0]
        if (file) {
            handleFileSelect(file)
        }
    }

    const handleDragOver = useCallback((event: React.DragEvent) => {
        event.preventDefault()
        setIsDragOver(true)
    }, [])

    const handleDragLeave = useCallback((event: React.DragEvent) => {
        event.preventDefault()
        setIsDragOver(false)
    }, [])

    const handleDrop = useCallback((event: React.DragEvent) => {
        event.preventDefault()
        setIsDragOver(false)

        const files = event.dataTransfer.files
        if (files.length > 0) {
            handleFileSelect(files[0])
        }
    }, [handleFileSelect])

    const handleRemove = useCallback(() => {
        setSelectedFile(null)
        setPreviewUrl(null)
        setError(null)
        if (onFileRemove) {
            onFileRemove()
        }
        if (fileInputRef.current) {
            fileInputRef.current.value = ''
        }
    }, [onFileRemove])

    const handleClick = () => {
        if (!disabled) {
            fileInputRef.current?.click()
        }
    }

    return (
        <div className={`space-y-4 ${className}`}>
            {!selectedFile ? (
                <div
                    onClick={handleClick}
                    onDragOver={handleDragOver}
                    onDragLeave={handleDragLeave}
                    onDrop={handleDrop}
                    className={`
                        border-2 border-dashed rounded-lg p-8 text-center transition-colors cursor-pointer
                        ${isDragOver
                            ? 'border-blue-400 bg-blue-50'
                            : 'border-gray-300 hover:border-blue-400'
                        }
                        ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
                    `}
                >
                    <UploadIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-lg font-medium text-gray-900 mb-2">{placeholder}</p>
                    <p className="text-gray-600 mb-4">
                        Drag and drop or click to browse
                    </p>
                    <p className="text-sm text-gray-500">
                        Supported formats: JPG, PNG, GIF (max {maxSize}MB)
                    </p>
                    <input
                        ref={fileInputRef}
                        type="file"
                        accept={acceptedTypes.join(',')}
                        onChange={handleFileInputChange}
                        className="hidden"
                        disabled={disabled}
                    />
                </div>
            ) : (
                <div className="relative bg-gray-100 rounded-lg p-4">
                    {showPreview && previewUrl && (
                        <div className="relative inline-block">
                            <img
                                src={previewUrl}
                                alt="Preview"
                                className="max-w-full h-auto rounded-lg max-h-64"
                            />
                            <button
                                onClick={handleRemove}
                                className="absolute top-2 right-2 bg-red-500 text-white p-1 rounded-full hover:bg-red-600 transition-colors"
                            >
                                <X className="h-4 w-4" />
                            </button>
                        </div>
                    )}
                    <div className="mt-4 flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                            <Image className="h-5 w-5 text-gray-500" />
                            <span className="text-sm font-medium text-gray-900">
                                {selectedFile.name}
                            </span>
                        </div>
                        <button
                            onClick={handleRemove}
                            className="text-sm text-red-600 hover:text-red-700"
                        >
                            Remove
                        </button>
                    </div>
                    <p className="text-xs text-gray-500 mt-1">
                        {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                </div>
            )}

            {error && (
                <div className="p-3 bg-red-50 border border-red-200 rounded-md">
                    <p className="text-sm text-red-600">{error}</p>
                </div>
            )}
        </div>
    )
}
