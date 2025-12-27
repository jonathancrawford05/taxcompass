'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

interface ExtractedFields {
  citizenship?: string[]
  current_country?: string
  destination_country?: string
  departure_date?: string
  marital_status?: 'single' | 'married' | 'common_law'
  has_spouse?: boolean
  spouse_location?: string
  has_dependents?: boolean
  owns_home_origin?: boolean
  home_disposition?: 'sell' | 'rent' | 'keep_vacant'
  owns_home_destination?: boolean
  employment_type?: 'employee' | 'self_employed' | 'business_owner'
  employer_country?: string
  annual_income?: string
  has_rental_property?: boolean
  investment_accounts_balance?: string
  rrsp_balance?: string
  tfsa_balance?: string
  unrealized_capital_gains?: string
}

interface ExtractionResult {
  filename: string
  file_size: number
  pages_processed: number
  extracted_fields: ExtractedFields
  confidence: number
  field_confidences: Record<string, number>
  document_type_detected: string
  warnings: string[]
}

interface FileUploadProps {
  onFieldsExtracted: (fields: ExtractedFields, result: ExtractionResult) => void
  apiBaseUrl?: string
}

export function FileUpload({ onFieldsExtracted, apiBaseUrl = 'http://localhost:8000' }: FileUploadProps) {
  const [uploading, setUploading] = useState(false)
  const [result, setResult] = useState<ExtractionResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setSelectedFile(file)
      setError(null)
      setResult(null)
    }
  }

  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Please select a file first')
      return
    }

    setUploading(true)
    setError(null)
    setResult(null)

    try {
      const formData = new FormData()
      formData.append('file', selectedFile)

      const response = await fetch(`${apiBaseUrl}/api/v1/documents/upload-and-extract`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Upload failed' }))
        throw new Error(errorData.detail || 'Upload failed')
      }

      const extractionResult: ExtractionResult = await response.json()
      setResult(extractionResult)

      // Notify parent component with extracted fields
      onFieldsExtracted(extractionResult.extracted_fields, extractionResult)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed')
    } finally {
      setUploading(false)
    }
  }

  const handleClear = () => {
    setSelectedFile(null)
    setResult(null)
    setError(null)
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Auto-Fill from Document</CardTitle>
        <CardDescription>
          Upload a pay stub, employment contract, or tax document to automatically extract information
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <label className="block text-sm font-medium">
            Select Document (PDF, PNG, JPG - max 10MB)
          </label>
          <div className="flex gap-2">
            <input
              type="file"
              accept=".pdf,.png,.jpg,.jpeg,.tiff,.bmp,.gif"
              onChange={handleFileSelect}
              className="flex-1 text-sm file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-primary file:text-primary-foreground hover:file:bg-primary/90"
              disabled={uploading}
            />
            {selectedFile && (
              <Button
                type="button"
                variant="outline"
                onClick={handleClear}
                disabled={uploading}
              >
                Clear
              </Button>
            )}
          </div>
          {selectedFile && (
            <p className="text-sm text-muted-foreground">
              Selected: {selectedFile.name} ({(selectedFile.size / 1024).toFixed(1)} KB)
            </p>
          )}
        </div>

        <Button
          type="button"
          onClick={handleUpload}
          disabled={!selectedFile || uploading}
          className="w-full"
        >
          {uploading ? 'Processing...' : 'Upload & Extract Data'}
        </Button>

        {error && (
          <div className="p-3 rounded-md bg-destructive/10 border border-destructive text-destructive text-sm">
            {error}
          </div>
        )}

        {result && (
          <div className="space-y-3 pt-2">
            <div className="p-3 rounded-md bg-green-50 border border-green-200">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-green-600 font-semibold">✓ Extraction Complete</span>
                <span className="text-sm text-muted-foreground">
                  ({(result.confidence * 100).toFixed(0)}% confidence)
                </span>
              </div>
              <div className="text-sm space-y-1">
                <p>
                  <span className="font-medium">File:</span> {result.filename}
                </p>
                <p>
                  <span className="font-medium">Type:</span> {result.document_type_detected}
                </p>
                <p>
                  <span className="font-medium">Pages:</span> {result.pages_processed}
                </p>
                <p>
                  <span className="font-medium">Fields extracted:</span>{' '}
                  {Object.keys(result.extracted_fields).length}
                </p>
              </div>
            </div>

            {Object.keys(result.extracted_fields).length > 0 && (
              <div className="p-3 rounded-md bg-blue-50 border border-blue-200">
                <p className="text-sm font-semibold text-blue-900 mb-2">Extracted Fields:</p>
                <div className="text-sm space-y-1">
                  {Object.entries(result.extracted_fields).map(([field, value]) => {
                    const confidence = result.field_confidences[field] || 0
                    return (
                      <div key={field} className="flex justify-between items-center">
                        <span className="font-medium text-blue-800">
                          {field.replace(/_/g, ' ')}:
                        </span>
                        <span className="text-blue-900">
                          {Array.isArray(value) ? value.join(', ') : String(value)}
                          <span className="ml-2 text-xs text-blue-600">
                            ({(confidence * 100).toFixed(0)}%)
                          </span>
                        </span>
                      </div>
                    )
                  })}
                </div>
              </div>
            )}

            {result.warnings.length > 0 && (
              <div className="p-3 rounded-md bg-orange-50 border border-orange-200">
                <p className="text-sm font-semibold text-orange-900 mb-2">Warnings:</p>
                <ul className="text-sm space-y-1 list-disc list-inside text-orange-800">
                  {result.warnings.map((warning, i) => (
                    <li key={i}>{warning}</li>
                  ))}
                </ul>
              </div>
            )}

            <p className="text-xs text-muted-foreground italic">
              Form fields have been auto-filled with the extracted data. Please review and adjust
              as needed.
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
