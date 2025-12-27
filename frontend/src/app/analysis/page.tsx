'use client'

import { useState } from 'react'
import { apiClient, type AnalysisRequest, type Analysis } from '@/lib/api'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { FileUpload } from '@/components/FileUpload'

export default function AnalysisPage() {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<Analysis | null>(null)
  const [error, setError] = useState<string | null>(null)

  const [formData, setFormData] = useState({
    title: 'Canada to UAE Tax Analysis',
    origin_country: 'CA',
    destination_country: 'AE',
    departure_date: '2025-06-01',
    citizenship: 'CA',
    current_country: 'CA',
    marital_status: 'married' as const,
    has_spouse: true,
    spouse_location: 'CA',
    has_dependents: false,
    owns_home_origin: true,
    home_disposition: 'rent' as const,
    owns_home_destination: false,
    employment_type: 'employee' as const,
    employer_country: 'AE',
    annual_income: '150000',
  })

  const handleFieldsExtracted = (extractedFields: any) => {
    // Auto-fill form with extracted fields
    setFormData((prev) => {
      const updated = { ...prev }

      // Map extracted fields to form fields
      if (extractedFields.citizenship && extractedFields.citizenship.length > 0) {
        updated.citizenship = extractedFields.citizenship[0]
      }
      if (extractedFields.current_country) {
        updated.current_country = extractedFields.current_country
      }
      if (extractedFields.destination_country) {
        updated.destination_country = extractedFields.destination_country
        updated.origin_country = extractedFields.current_country || prev.origin_country
      }
      if (extractedFields.departure_date) {
        updated.departure_date = extractedFields.departure_date
      }
      if (extractedFields.marital_status) {
        updated.marital_status = extractedFields.marital_status
      }
      if (extractedFields.has_spouse !== undefined) {
        updated.has_spouse = extractedFields.has_spouse
      }
      if (extractedFields.spouse_location) {
        updated.spouse_location = extractedFields.spouse_location
      }
      if (extractedFields.has_dependents !== undefined) {
        updated.has_dependents = extractedFields.has_dependents
      }
      if (extractedFields.owns_home_origin !== undefined) {
        updated.owns_home_origin = extractedFields.owns_home_origin
      }
      if (extractedFields.home_disposition) {
        updated.home_disposition = extractedFields.home_disposition
      }
      if (extractedFields.owns_home_destination !== undefined) {
        updated.owns_home_destination = extractedFields.owns_home_destination
      }
      if (extractedFields.employment_type) {
        updated.employment_type = extractedFields.employment_type
      }
      if (extractedFields.employer_country) {
        updated.employer_country = extractedFields.employer_country
      }
      if (extractedFields.annual_income) {
        updated.annual_income = String(extractedFields.annual_income)
      }

      return updated
    })

    // Clear any previous errors
    setError(null)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const request: AnalysisRequest = {
        title: formData.title,
        origin_country: formData.origin_country,
        destination_country: formData.destination_country,
        departure_date: formData.departure_date,
        user_profile: {
          citizenship: [formData.citizenship],
          current_country: formData.current_country,
          destination_country: formData.destination_country,
          departure_date: formData.departure_date,
          marital_status: formData.marital_status,
          has_spouse: formData.has_spouse,
          spouse_location: formData.has_spouse ? formData.spouse_location : undefined,
          has_dependents: formData.has_dependents,
          owns_home_origin: formData.owns_home_origin,
          home_disposition: formData.owns_home_origin ? formData.home_disposition : undefined,
          owns_home_destination: formData.owns_home_destination,
          employment_type: formData.employment_type,
          employer_country: formData.employer_country,
          annual_income: formData.annual_income,
        },
      }

      const analysis = await apiClient.quickAnalysis(request)
      setResult(analysis)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container mx-auto py-8 px-4 max-w-4xl">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">Tax Residency Analysis</h1>
        <p className="text-muted-foreground">
          AI-powered analysis for cross-border tax residency determination
        </p>
      </div>

      <div className="mb-6">
        <FileUpload onFieldsExtracted={handleFieldsExtracted} />
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Basic Information</CardTitle>
            <CardDescription>Tell us about your move</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Analysis Title</label>
              <Input
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                placeholder="e.g., Canada to UAE Move"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Origin Country</label>
                <Input
                  value={formData.origin_country}
                  onChange={(e) => setFormData({ ...formData, origin_country: e.target.value })}
                  placeholder="CA"
                  maxLength={2}
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Destination Country</label>
                <Input
                  value={formData.destination_country}
                  onChange={(e) => setFormData({ ...formData, destination_country: e.target.value })}
                  placeholder="AE"
                  maxLength={2}
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Departure Date</label>
              <Input
                type="date"
                value={formData.departure_date}
                onChange={(e) => setFormData({ ...formData, departure_date: e.target.value })}
              />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Personal Details</CardTitle>
            <CardDescription>Family and property information</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Marital Status</label>
                <select
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background"
                  value={formData.marital_status}
                  onChange={(e) => setFormData({ ...formData, marital_status: e.target.value as any })}
                >
                  <option value="single">Single</option>
                  <option value="married">Married</option>
                  <option value="common_law">Common Law</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Spouse Location</label>
                <Input
                  value={formData.spouse_location}
                  onChange={(e) => setFormData({ ...formData, spouse_location: e.target.value })}
                  placeholder="CA"
                  disabled={!formData.has_spouse}
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Owns Home in Origin</label>
                <select
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background"
                  value={formData.owns_home_origin ? 'yes' : 'no'}
                  onChange={(e) => setFormData({ ...formData, owns_home_origin: e.target.value === 'yes' })}
                >
                  <option value="yes">Yes</option>
                  <option value="no">No</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Home Disposition</label>
                <select
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background"
                  value={formData.home_disposition}
                  onChange={(e) => setFormData({ ...formData, home_disposition: e.target.value as any })}
                  disabled={!formData.owns_home_origin}
                >
                  <option value="sell">Sell</option>
                  <option value="rent">Rent</option>
                  <option value="keep_vacant">Keep Vacant</option>
                </select>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Employment & Income</CardTitle>
            <CardDescription>Work and financial information</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Employment Type</label>
                <select
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background"
                  value={formData.employment_type}
                  onChange={(e) => setFormData({ ...formData, employment_type: e.target.value as any })}
                >
                  <option value="employee">Employee</option>
                  <option value="self_employed">Self Employed</option>
                  <option value="business_owner">Business Owner</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Employer Country</label>
                <Input
                  value={formData.employer_country}
                  onChange={(e) => setFormData({ ...formData, employer_country: e.target.value })}
                  placeholder="AE"
                  maxLength={2}
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Annual Income (USD)</label>
              <Input
                type="number"
                value={formData.annual_income}
                onChange={(e) => setFormData({ ...formData, annual_income: e.target.value })}
                placeholder="150000"
              />
            </div>
          </CardContent>
        </Card>

        <Button type="submit" className="w-full" size="lg" disabled={loading}>
          {loading ? 'Analyzing...' : 'Run Analysis'}
        </Button>
      </form>

      {error && (
        <Card className="mt-6 border-destructive">
          <CardHeader>
            <CardTitle className="text-destructive">Error</CardTitle>
          </CardHeader>
          <CardContent>
            <p>{error}</p>
          </CardContent>
        </Card>
      )}

      {result && (
        <div className="mt-8 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Analysis Results</CardTitle>
              <CardDescription>
                Completed on {new Date(result.completed_at || '').toLocaleString()}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h3 className="font-semibold mb-2">{result.origin_country} Residency</h3>
                  <p className="text-2xl font-bold capitalize">{result.origin_residency_status}</p>
                </div>
                <div>
                  <h3 className="font-semibold mb-2">{result.destination_country} Residency</h3>
                  <p className="text-2xl font-bold capitalize">{result.destination_residency_status}</p>
                </div>
              </div>

              <div>
                <h3 className="font-semibold mb-2">Confidence Score</h3>
                <div className="flex items-center gap-2">
                  <div className="flex-1 bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full"
                      style={{ width: `${(result.confidence_score || 0) * 100}%` }}
                    />
                  </div>
                  <span className="text-sm font-medium">
                    {((result.confidence_score || 0) * 100).toFixed(0)}%
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>

          {result.recommendations && result.recommendations.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Recommendations</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  {result.recommendations.map((rec, i) => (
                    <li key={i} className="flex gap-2">
                      <span className="text-blue-600">•</span>
                      <span>{rec}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          )}

          {result.red_flags && result.red_flags.length > 0 && (
            <Card className="border-orange-200">
              <CardHeader>
                <CardTitle className="text-orange-600">Red Flags</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  {result.red_flags.map((flag, i) => (
                    <li key={i} className="flex gap-2">
                      <span className="text-orange-600">⚠️</span>
                      <span>{flag}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          )}

          {result.reasoning && (
            <Card>
              <CardHeader>
                <CardTitle>Detailed Reasoning</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="prose prose-sm max-w-none whitespace-pre-wrap">
                  {result.reasoning}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </div>
  )
}
