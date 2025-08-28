import Link from 'next/link'
import { ArrowRight, Search, Zap, Shield, BarChart3, Users, CheckCircle } from 'lucide-react'

export default function Home() {
    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
            {/* Navigation */}
            <nav className="bg-white/80 backdrop-blur-md border-b border-gray-200 sticky top-0 z-50">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between items-center h-16">
                        <div className="flex items-center">
                            <Search className="h-8 w-8 text-blue-600 mr-3" />
                            <span className="text-xl font-bold text-gray-900">VisualSearch</span>
                        </div>
                        <div className="hidden md:flex items-center space-x-8">
                            <a href="#features" className="text-gray-600 hover:text-blue-600 transition-colors">Features</a>
                            <a href="#pricing" className="text-gray-600 hover:text-blue-600 transition-colors">Pricing</a>
                            <a href="#about" className="text-gray-600 hover:text-blue-600 transition-colors">About</a>
                        </div>
                        <div className="flex items-center space-x-4">
                            <Link href="/auth/signin" className="text-gray-600 hover:text-blue-600 transition-colors">
                                Sign In
                            </Link>
                            <Link href="/auth/register" className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
                                Get Started
                            </Link>
                        </div>
                    </div>
                </div>
            </nav>

            {/* Hero Section */}
            <section className="relative overflow-hidden">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16">
                    <div className="text-center">
                        <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
                            Find Products with
                            <span className="text-blue-600"> Visual Search</span>
                        </h1>
                        <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
                            Transform your e-commerce experience with AI-powered image search.
                            Upload any image and instantly find similar products from your catalog.
                        </p>
                        <div className="flex flex-col sm:flex-row gap-4 justify-center">
                            <Link href="/auth/register" className="bg-blue-600 text-white px-8 py-4 rounded-lg text-lg font-semibold hover:bg-blue-700 transition-colors flex items-center justify-center">
                                Start Free Trial
                                <ArrowRight className="ml-2 h-5 w-5" />
                            </Link>
                            <Link href="/demo" className="border border-gray-300 text-gray-700 px-8 py-4 rounded-lg text-lg font-semibold hover:border-blue-600 hover:text-blue-600 transition-colors">
                                Try Demo
                            </Link>
                        </div>
                    </div>
                </div>

                {/* Hero Image */}
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-20">
                    <div className="relative">
                        <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-4xl mx-auto">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
                                <div>
                                    <h3 className="text-2xl font-semibold text-gray-900 mb-4">
                                        Upload an Image
                                    </h3>
                                    <p className="text-gray-600 mb-6">
                                        Simply drag and drop or click to upload any product image
                                    </p>
                                    <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-400 transition-colors cursor-pointer">
                                        <Search className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                                        <p className="text-gray-600">Click to upload or drag and drop</p>
                                        <p className="text-sm text-gray-500 mt-2">PNG, JPG up to 10MB</p>
                                    </div>
                                </div>
                                <div>
                                    <h3 className="text-2xl font-semibold text-gray-900 mb-4">
                                        Get Instant Results
                                    </h3>
                                    <p className="text-gray-600 mb-6">
                                        AI finds the most similar products from your catalog
                                    </p>
                                    <div className="grid grid-cols-2 gap-4">
                                        {[1, 2, 3, 4].map((i) => (
                                            <div key={i} className="bg-gray-100 rounded-lg p-4 text-center">
                                                <div className="w-16 h-16 bg-gray-200 rounded-lg mx-auto mb-2"></div>
                                                <p className="text-sm font-medium text-gray-700">Product {i}</p>
                                                <p className="text-xs text-gray-500">$99.99</p>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Features Section */}
            <section id="features" className="py-20 bg-white">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="text-center mb-16">
                        <h2 className="text-4xl font-bold text-gray-900 mb-4">
                            Powerful Features for Modern E-commerce
                        </h2>
                        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
                            Everything you need to implement visual search and boost your conversion rates
                        </p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                        <div className="bg-gray-50 rounded-xl p-8">
                            <Zap className="h-12 w-12 text-blue-600 mb-6" />
                            <h3 className="text-xl font-semibold text-gray-900 mb-4">Lightning Fast Search</h3>
                            <p className="text-gray-600">
                                Get search results in milliseconds with our optimized vector database and AI models.
                            </p>
                        </div>

                        <div className="bg-gray-50 rounded-xl p-8">
                            <Shield className="h-12 w-12 text-blue-600 mb-6" />
                            <h3 className="text-xl font-semibold text-gray-900 mb-4">Enterprise Security</h3>
                            <p className="text-gray-600">
                                Bank-level security with role-based access control and data encryption at rest.
                            </p>
                        </div>

                        <div className="bg-gray-50 rounded-xl p-8">
                            <BarChart3 className="h-12 w-12 text-blue-600 mb-6" />
                            <h3 className="text-xl font-semibold text-gray-900 mb-4">Advanced Analytics</h3>
                            <p className="text-gray-600">
                                Track search performance, user behavior, and conversion rates with detailed insights.
                            </p>
                        </div>

                        <div className="bg-gray-50 rounded-xl p-8">
                            <Users className="h-12 w-12 text-blue-600 mb-6" />
                            <h3 className="text-xl font-semibold text-gray-900 mb-4">Multi-tenant Ready</h3>
                            <p className="text-gray-600">
                                Built for scale with support for multiple organizations and teams.
                            </p>
                        </div>

                        <div className="bg-gray-50 rounded-xl p-8">
                            <Search className="h-12 w-12 text-blue-600 mb-6" />
                            <h3 className="text-xl font-semibold text-gray-900 mb-4">Smart Filters</h3>
                            <p className="text-gray-600">
                                Combine visual search with traditional filters like price, category, and brand.
                            </p>
                        </div>

                        <div className="bg-gray-50 rounded-xl p-8">
                            <CheckCircle className="h-12 w-12 text-blue-600 mb-6" />
                            <h3 className="text-xl font-semibold text-gray-900 mb-4">Easy Integration</h3>
                            <p className="text-gray-600">
                                Simple API integration with comprehensive documentation and SDKs.
                            </p>
                        </div>
                    </div>
                </div>
            </section>

            {/* Pricing Section */}
            <section id="pricing" className="py-20 bg-gray-50">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="text-center mb-16">
                        <h2 className="text-4xl font-bold text-gray-900 mb-4">
                            Simple, Transparent Pricing
                        </h2>
                        <p className="text-xl text-gray-600">
                            Choose the plan that fits your business needs
                        </p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                        {/* Starter Plan */}
                        <div className="bg-white rounded-2xl shadow-lg p-8">
                            <div className="text-center">
                                <h3 className="text-2xl font-semibold text-gray-900 mb-2">Starter</h3>
                                <div className="text-4xl font-bold text-gray-900 mb-2">$99</div>
                                <p className="text-gray-600 mb-8">per month</p>
                            </div>
                            <ul className="space-y-4 mb-8">
                                <li className="flex items-center">
                                    <CheckCircle className="h-5 w-5 text-green-500 mr-3" />
                                    <span>Up to 10,000 products</span>
                                </li>
                                <li className="flex items-center">
                                    <CheckCircle className="h-5 w-5 text-green-500 mr-3" />
                                    <span>1,000 searches/month</span>
                                </li>
                                <li className="flex items-center">
                                    <CheckCircle className="h-5 w-5 text-green-500 mr-3" />
                                    <span>Basic analytics</span>
                                </li>
                                <li className="flex items-center">
                                    <CheckCircle className="h-5 w-5 text-green-500 mr-3" />
                                    <span>Email support</span>
                                </li>
                            </ul>
                            <Link href="/auth/register" className="w-full bg-gray-900 text-white py-3 rounded-lg font-semibold hover:bg-gray-800 transition-colors block text-center">
                                Get Started
                            </Link>
                        </div>

                        {/* Professional Plan */}
                        <div className="bg-white rounded-2xl shadow-xl p-8 border-2 border-blue-600 relative">
                            <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                                <span className="bg-blue-600 text-white px-4 py-1 rounded-full text-sm font-semibold">
                                    Most Popular
                                </span>
                            </div>
                            <div className="text-center">
                                <h3 className="text-2xl font-semibold text-gray-900 mb-2">Professional</h3>
                                <div className="text-4xl font-bold text-gray-900 mb-2">$299</div>
                                <p className="text-gray-600 mb-8">per month</p>
                            </div>
                            <ul className="space-y-4 mb-8">
                                <li className="flex items-center">
                                    <CheckCircle className="h-5 w-5 text-green-500 mr-3" />
                                    <span>Up to 100,000 products</span>
                                </li>
                                <li className="flex items-center">
                                    <CheckCircle className="h-5 w-5 text-green-500 mr-3" />
                                    <span>10,000 searches/month</span>
                                </li>
                                <li className="flex items-center">
                                    <CheckCircle className="h-5 w-5 text-green-500 mr-3" />
                                    <span>Advanced analytics</span>
                                </li>
                                <li className="flex items-center">
                                    <CheckCircle className="h-5 w-5 text-green-500 mr-3" />
                                    <span>Priority support</span>
                                </li>
                                <li className="flex items-center">
                                    <CheckCircle className="h-5 w-5 text-green-500 mr-3" />
                                    <span>Custom integrations</span>
                                </li>
                            </ul>
                            <Link href="/auth/register" className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors block text-center">
                                Get Started
                            </Link>
                        </div>

                        {/* Enterprise Plan */}
                        <div className="bg-white rounded-2xl shadow-lg p-8">
                            <div className="text-center">
                                <h3 className="text-2xl font-semibold text-gray-900 mb-2">Enterprise</h3>
                                <div className="text-4xl font-bold text-gray-900 mb-2">Custom</div>
                                <p className="text-gray-600 mb-8">contact sales</p>
                            </div>
                            <ul className="space-y-4 mb-8">
                                <li className="flex items-center">
                                    <CheckCircle className="h-5 w-5 text-green-500 mr-3" />
                                    <span>Unlimited products</span>
                                </li>
                                <li className="flex items-center">
                                    <CheckCircle className="h-5 w-5 text-green-500 mr-3" />
                                    <span>Unlimited searches</span>
                                </li>
                                <li className="flex items-center">
                                    <CheckCircle className="h-5 w-5 text-green-500 mr-3" />
                                    <span>Custom AI models</span>
                                </li>
                                <li className="flex items-center">
                                    <CheckCircle className="h-5 w-5 text-green-500 mr-3" />
                                    <span>Dedicated support</span>
                                </li>
                                <li className="flex items-center">
                                    <CheckCircle className="h-5 w-5 text-green-500 mr-3" />
                                    <span>SLA guarantee</span>
                                </li>
                            </ul>
                            <Link href="/contact" className="w-full bg-gray-900 text-white py-3 rounded-lg font-semibold hover:bg-gray-800 transition-colors block text-center">
                                Contact Sales
                            </Link>
                        </div>
                    </div>
                </div>
            </section>

            {/* CTA Section */}
            <section className="py-20 bg-blue-600">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
                    <h2 className="text-4xl font-bold text-white mb-4">
                        Ready to Transform Your E-commerce?
                    </h2>
                    <p className="text-xl text-blue-100 mb-8 max-w-3xl mx-auto">
                        Join thousands of businesses using visual search to increase conversions and improve customer experience.
                    </p>
                    <div className="flex flex-col sm:flex-row gap-4 justify-center">
                        <Link href="/auth/register" className="bg-white text-blue-600 px-8 py-4 rounded-lg text-lg font-semibold hover:bg-gray-100 transition-colors">
                            Start Free Trial
                        </Link>
                        <Link href="/demo" className="border border-white text-white px-8 py-4 rounded-lg text-lg font-semibold hover:bg-white hover:text-blue-600 transition-colors">
                            Schedule Demo
                        </Link>
                    </div>
                </div>
            </section>

            {/* Footer */}
            <footer className="bg-gray-900 text-white py-12">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
                        <div>
                            <div className="flex items-center mb-4">
                                <Search className="h-8 w-8 text-blue-400 mr-3" />
                                <span className="text-xl font-bold">VisualSearch</span>
                            </div>
                            <p className="text-gray-400">
                                AI-powered visual search for modern e-commerce platforms.
                            </p>
                        </div>
                        <div>
                            <h3 className="text-lg font-semibold mb-4">Product</h3>
                            <ul className="space-y-2 text-gray-400">
                                <li><a href="#features" className="hover:text-white transition-colors">Features</a></li>
                                <li><a href="/pricing" className="hover:text-white transition-colors">Pricing</a></li>
                                <li><a href="/docs" className="hover:text-white transition-colors">Documentation</a></li>
                                <li><a href="/api" className="hover:text-white transition-colors">API</a></li>
                            </ul>
                        </div>
                        <div>
                            <h3 className="text-lg font-semibold mb-4">Company</h3>
                            <ul className="space-y-2 text-gray-400">
                                <li><a href="/about" className="hover:text-white transition-colors">About</a></li>
                                <li><a href="/blog" className="hover:text-white transition-colors">Blog</a></li>
                                <li><a href="/careers" className="hover:text-white transition-colors">Careers</a></li>
                                <li><a href="/contact" className="hover:text-white transition-colors">Contact</a></li>
                            </ul>
                        </div>
                        <div>
                            <h3 className="text-lg font-semibold mb-4">Support</h3>
                            <ul className="space-y-2 text-gray-400">
                                <li><a href="/help" className="hover:text-white transition-colors">Help Center</a></li>
                                <li><a href="/status" className="hover:text-white transition-colors">Status</a></li>
                                <li><a href="/security" className="hover:text-white transition-colors">Security</a></li>
                                <li><a href="/privacy" className="hover:text-white transition-colors">Privacy</a></li>
                            </ul>
                        </div>
                    </div>
                    <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
                        <p>&copy; 2024 VisualSearch. All rights reserved.</p>
                    </div>
                </div>
            </footer>
        </div>
    )
}
