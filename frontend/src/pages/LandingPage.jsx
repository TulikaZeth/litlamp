import { Button } from '../components/ui/button';
import { Card } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { 
  BookOpen, 
  Upload, 
  MessageSquare, 
  FileText, 
  Zap, 
  Shield, 
  Database, 
  Cloud,
  Code,
  CheckCircle,
  ArrowRight,
  Github,
  ExternalLink
} from 'lucide-react';
import { Link } from 'react-router-dom';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background text-foreground relative overflow-hidden">
      {/* Grid Background with Depth */}
      <div className="absolute inset-0 pointer-events-none">
        {/* Large grid layer */}
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808018_2px,transparent_2px),linear-gradient(to_bottom,#80808018_2px,transparent_2px)] bg-[size:80px_80px]" />
        {/* Medium grid layer with slight offset for depth */}
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:40px_40px] opacity-60" />
        {/* Radial gradient for depth effect */}
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,transparent_0%,rgba(0,0,0,0.3)_100%)]" />
      </div>
      <div className="relative z-10">
      {/* Navigation */}
      <nav className="border-b border-border sticky top-0 bg-background/95 backdrop-blur z-50">
        <div className="container mx-auto px-4 sm:px-6 py-3 sm:py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <BookOpen size={24} className="text-primary sm:w-7 sm:h-7" />
              <span className="text-lg sm:text-xl font-bold">Literate-Lamp</span>
            </div>
            <div className="flex items-center gap-3 sm:gap-6">
              <a href="#features" className="hidden sm:inline text-sm hover:text-primary transition-colors">Features</a>
              <a href="#tech" className="hidden sm:inline text-sm hover:text-primary transition-colors">Tech Stack</a>
              <a href="#security" className="hidden md:inline text-sm hover:text-primary transition-colors">Security</a>
              <Link to="/app">
                <Button className="gap-1 sm:gap-2 text-sm px-3 sm:px-4">
                  <span className="hidden xs:inline">Get Started</span>
                  <span className="xs:hidden">Start</span>
                  <ArrowRight size={14} className="sm:w-4 sm:h-4" />
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="container mx-auto px-4 sm:px-6 py-12 sm:py-16 md:py-20">
        <div className="max-w-4xl mx-auto text-center">
          <Badge variant="outline" className="mb-4 sm:mb-6 border-green-500 text-green-500 text-xs sm:text-sm px-3 py-1">
            <span className="hidden sm:inline">Session-Only Storage • Zero Data Persistence • 100% Private</span>
            <span className="sm:hidden">Session-Only • Zero Persistence</span>
          </Badge>
          <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold mb-4 sm:mb-6 leading-tight px-4 sm:px-0">
            Multimodal Document Q&A with Advanced RAG
          </h1>
          <p className="text-base sm:text-lg md:text-xl text-muted-foreground mb-6 sm:mb-8 leading-relaxed px-2 sm:px-0">
            <span className="text-foreground font-semibold">Your documents are never saved.</span> Upload, ask questions, and get accurate answers with citations. 
            All data exists only during your session and is automatically cleared when you close the application.
          </p>
          <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 justify-center px-4 sm:px-0">
            <Link to="/app" className="w-full sm:w-auto">
              <Button size="lg" className="gap-2 w-full sm:w-auto">
                Launch Application
                <ArrowRight size={18} />
              </Button>
            </Link>
            <a href="https://github.com/TulikaZeth/literate-lamp" target="_blank" rel="noopener noreferrer" className="w-full sm:w-auto">
              <Button size="lg" variant="primary" className="gap-2 !bg-black/70 w-full sm:w-auto">
                <Github size={18} />
                View on GitHub
              </Button>
            </a>
          </div>
          <div className="mt-8 sm:mt-12 grid grid-cols-2 sm:flex sm:flex-wrap items-center justify-center gap-4 sm:gap-6 md:gap-8 text-xs sm:text-sm text-muted-foreground px-4">
            <div className="flex items-center gap-2">
              <CheckCircle size={14} className="text-green-500 sm:w-4 sm:h-4 shrink-0" />
              <span className="font-semibold text-foreground text-xs sm:text-sm">Session-Only</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle size={14} className="text-green-500 sm:w-4 sm:h-4 shrink-0" />
              <span className="font-semibold text-foreground text-xs sm:text-sm">No Persistence</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle size={14} className="text-green-500 sm:w-4 sm:h-4 shrink-0" />
              <span className="text-xs sm:text-sm">300MB RAM</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle size={14} className="text-green-500 sm:w-4 sm:h-4 shrink-0" />
              <span className="text-xs sm:text-sm">Free Tier</span>
            </div>
          </div>
        </div>
      </section>

      {/* Key Features */}
      <section id="features" className="border-t border-border py-12 sm:py-16 md:py-20 bg-card">
        <div className="container mx-auto px-4 sm:px-6">
          <div className="text-center mb-8 sm:mb-12">
            <h2 className="text-2xl sm:text-3xl font-bold mb-3 sm:mb-4">Core Features</h2>
            <p className="text-sm sm:text-base text-muted-foreground max-w-2xl mx-auto px-4">
              Session-only RAG system with multimodal support and zero data persistence
            </p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
            <Card className="p-6 hover:border-primary transition-colors bg-black">
              <Upload className="text-primary mb-4" size={32} />
              <h3 className="text-lg font-semibold mb-2">Multimodal Upload</h3>
              <p className="text-sm text-muted-foreground">
                Support for PDF, TXT, MD, DOCX, and image files. Single endpoint for upload and query.
              </p>
            </Card>

            <Card className="p-6 hover:border-primary transition-colors bg-black">
              <MessageSquare className="text-primary mb-4" size={32} />
              <h3 className="text-lg font-semibold mb-2">Smart Q&A</h3>
              <p className="text-sm text-muted-foreground">
                Ask questions and receive accurate answers with source citations and excerpts.
              </p>
            </Card>

            <Card className="p-6 hover:border-primary transition-colors bg-black">
              <Zap className="text-primary mb-4" size={32} />
              <h3 className="text-lg font-semibold mb-2">Advanced NLP</h3>
              <p className="text-sm text-muted-foreground">
                PyTorch-based language models with fast inference. Sentence embeddings and semantic understanding.
              </p>
            </Card>

            <Card className="p-6 hover:border-primary transition-colors bg-black">
              <Database className="text-primary mb-4" size={32} />
              <h3 className="text-lg font-semibold mb-2">In-Memory Only</h3>
              <p className="text-sm text-muted-foreground">
                ChromaDB configured for RAM-only operation. No disk writes, no persistence. Data vanishes when session ends.
              </p>
            </Card>

            <Card className="p-6 hover:border-primary transition-colors bg-black">
              <Cloud className="text-primary mb-4" size={32} />
              <h3 className="text-lg font-semibold mb-2">Cloud Ready</h3>
              <p className="text-sm text-muted-foreground">
                Optimized for Render free tier. Deploy to AWS, GCP, or Azure with Docker.
              </p>
            </Card>

            <Card className="p-6 hover:border-primary transition-colors bg-black">
              <Shield className="text-primary mb-4" size={32} />
              <h3 className="text-lg font-semibold mb-2">Session-Only Privacy</h3>
              <p className="text-sm text-muted-foreground">
                Documents exist only during your active session. No database storage, no persistence. Close the app, and all data is gone forever.
              </p>
            </Card>
          </div>
        </div>
      </section>

      {/* Memory Optimization */}
      <section className="py-12 sm:py-16 md:py-20">
        <div className="container mx-auto px-4 sm:px-6">
          <div className="max-w-4xl mx-auto">
            <div className="text-center mb-8 sm:mb-12">
              <h2 className="text-2xl sm:text-3xl font-bold mb-3 sm:mb-4">Memory Optimized Architecture</h2>
              <p className="text-sm sm:text-base text-muted-foreground px-4">
                Reduced from 3GB to 300MB RAM usage through strategic optimization
              </p>
            </div>
            {/* <Card className="p-4 sm:p-6 md:p-8 bg-black">
              <div className="grid md:grid-cols-2 gap-8">
                <div>
                  <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
                    <span className="text-red-500">Removed</span>
                  </h3>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-sm">PyTorch + Transformers</span>
                      <Badge variant="destructive">-2GB</Badge>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm">Sentence Transformers</span>
                      <Badge variant="destructive">-500MB</Badge>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm">FAISS CPU</span>
                      <Badge variant="destructive">-200MB</Badge>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm">Tesseract OCR</span>
                      <Badge variant="destructive">-150MB</Badge>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm">Cross-Encoder</span>
                      <Badge variant="destructive">-100MB</Badge>
                    </div>
                  </div>
                </div>
                <div>
                  <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
                    <span className="text-green-500">Added</span>
                  </h3>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-sm">Gemini Embeddings API</span>
                      <Badge variant="outline" className="text-green-500 border-green-500">0MB</Badge>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm">Lazy Loading</span>
                      <Badge variant="outline" className="text-green-500 border-green-500">On-demand</Badge>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm">ChromaDB Only</span>
                      <Badge variant="outline" className="text-green-500 border-green-500">~150MB</Badge>
                    </div>
                  </div>
                  <div className="mt-8 p-4 bg-primary/10 border border-primary rounded-lg">
                    <div className="flex justify-between items-center">
                      <span className="font-semibold">Total Runtime</span>
                      <Badge className="text-lg">~300MB</Badge>
                    </div>
                  </div>
                </div>
              </div>
            </Card> */}
          </div>
        </div>
      </section>

      {/* Tech Stack */}
      <section id="tech" className="border-t border-border py-12 sm:py-16 md:py-20 bg-card">
        <div className="container mx-auto px-4 sm:px-6">
          <div className="text-center mb-8 sm:mb-12">
            <h2 className="text-2xl sm:text-3xl font-bold mb-3 sm:mb-4">Technology Stack</h2>
            <p className="text-sm sm:text-base text-muted-foreground px-4">
              Built with modern, production-ready technologies
            </p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-5xl mx-auto">
            <Card className="p-6 text-center bg-black">
              <Code className="mx-auto mb-3 text-primary" size={32} />
              <h3 className="font-semibold mb-2">FastAPI</h3>
              <p className="text-xs text-muted-foreground">REST API Framework</p>
            </Card>
            <Card className="p-6 text-center bg-black">
              <Code className="mx-auto mb-3 text-primary" size={32} />
              <h3 className="font-semibold mb-2">PyTorch</h3>
              <p className="text-xs text-muted-foreground">Deep Learning Framework</p>
            </Card>
            <Card className="p-6 text-center bg-black">
              <Database className="mx-auto mb-3 text-primary" size={32} />
              <h3 className="font-semibold mb-2">ChromaDB</h3>
              <p className="text-xs text-muted-foreground">Vector Database</p>
            </Card>
            <Card className="p-6 text-center bg-black">
              <Code className="mx-auto mb-3 text-primary" size={32} />
              <h3 className="font-semibold mb-2">Sentence Transformers</h3>
              <p className="text-xs text-muted-foreground">Semantic Embeddings</p>
            </Card>
            <Card className="p-6 text-center bg-black">
              <Database className="mx-auto mb-3 text-primary" size={32} />
              <h3 className="font-semibold mb-2">FAISS</h3>
              <p className="text-xs text-muted-foreground">Vector Search</p>
            </Card>
            <Card className="p-6 text-center bg-black">
              <FileText className="mx-auto mb-3 text-primary" size={32} />
              <h3 className="font-semibold mb-2">Tesseract OCR</h3>
              <p className="text-xs text-muted-foreground">Document Processing</p>
            </Card>
            <Card className="p-6 text-center bg-black">
              <BookOpen className="mx-auto mb-3 text-primary" size={32} />
              <h3 className="font-semibold mb-2">LangChain</h3>
              <p className="text-xs text-muted-foreground">RAG Orchestration</p>
            </Card>
          </div>
        </div>
      </section>

      {/* Security Section */}
      <section id="security" className="py-12 sm:py-16 md:py-20">
        <div className="container mx-auto px-4 sm:px-6">
          <div className="max-w-4xl mx-auto">
            <div className="text-center mb-8 sm:mb-12">
              <h2 className="text-2xl sm:text-3xl font-bold mb-3 sm:mb-4 px-4">Session-Only Storage: Our Core Feature</h2>
              <p className="text-sm sm:text-base text-muted-foreground px-4">
                <span className="text-foreground font-semibold">Zero data persistence.</span> Your documents are never saved to any database.
              </p>
            </div>
            <Card className="p-4 sm:p-6 md:p-8 border-green-500/30 bg-black">
              <div className="space-y-6">
                <div className="flex items-start gap-4">
                  <Shield className="text-green-500 shrink-0 mt-1" size={24} />
                  <div>
                    <h3 className="text-lg font-semibold mb-2">Ephemeral by Design</h3>
                    <p className="text-sm text-muted-foreground leading-relaxed">
                      When you upload documents, they exist <span className="text-foreground font-semibold">only in active memory during your current session</span>. 
                      The moment you close the application or refresh the page, all documents, embeddings, and chat history are permanently deleted. 
                      There is no database persistence, no file storage, no recovery possible.
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-4">
                  <Database className="text-green-500 shrink-0 mt-1" size={24} />
                  <div>
                    <h3 className="text-lg font-semibold mb-2">No Database, No Traces</h3>
                    <p className="text-sm text-muted-foreground leading-relaxed">
                      Unlike traditional RAG systems that store embeddings in persistent vector databases, Literate-Lamp keeps everything in RAM. 
                      ChromaDB is configured for <span className="text-foreground font-semibold">in-memory operation only</span>—no files written to disk, no residual data, no audit trails. 
                      Your sensitive documents leave zero footprint.
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-4">
                  <Code className="text-green-500 shrink-0 mt-1" size={24} />
                  <div>
                    <h3 className="text-lg font-semibold mb-2">Local Processing Only</h3>
                    <p className="text-sm text-muted-foreground leading-relaxed">
                      All document processing, text extraction, and chunking happens locally on your machine. 
                      We use PyTorch, Sentence Transformers, FAISS, and Tesseract OCR for complete local processing—document content never leaves your system. 
                      No third-party services ever see your raw documents.
                    </p>
                  </div>
                </div>
                <div className="mt-8 p-6 bg-green-500/10 border border-green-500 rounded-lg">
                  <div className="text-center space-y-2">
                    <p className="text-lg font-semibold text-green-500">
                      Perfect for Sensitive Documents
                    </p>
                    <p className="text-sm text-muted-foreground">
                      Legal contracts, medical records, financial reports, confidential research—analyze anything without leaving a trace. 
                      Session closes, data vanishes. Simple as that.
                    </p>
                  </div>
                </div>
              </div>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="border-t border-border py-12 sm:py-16 md:py-20 bg-card">
        <div className="container mx-auto px-4 sm:px-6">
          <div className="max-w-3xl mx-auto text-center">
            <h2 className="text-2xl sm:text-3xl font-bold mb-3 sm:mb-4">Ready to Get Started?</h2>
            <p className="text-sm sm:text-base text-muted-foreground mb-6 sm:mb-8 px-4">
              Deploy your own RAG system in minutes. Free tier ready with comprehensive documentation.
            </p>
            <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 justify-center px-4">
              <Link to="/app" className="w-full sm:w-auto">
                <Button size="lg" className="gap-2 w-full sm:w-auto">
                  Launch Application
                  <ArrowRight size={18} />
                </Button>
              </Link>
              <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer" className="w-full sm:w-auto">
                <Button size="lg" variant="outline" className="gap-2 w-full sm:w-auto">
                  <FileText size={18} />
                  <span className="hidden xs:inline">API Documentation</span>
                  <span className="xs:hidden">API Docs</span>
                  <ExternalLink size={14} />
                </Button>
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border py-6 sm:py-8">
        <div className="container mx-auto px-4 sm:px-6">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <BookOpen size={20} className="text-primary sm:w-6 sm:h-6" />
              <span className="font-semibold text-sm sm:text-base">Literate-Lamp</span>
            </div>
            <div className="flex items-center gap-4 sm:gap-6 text-xs sm:text-sm text-muted-foreground">
              <a href="https://github.com/TulikaZeth/literate-lamp" target="_blank" rel="noopener noreferrer" className="hover:text-foreground transition-colors flex items-center gap-1">
                <Github size={14} className="sm:w-4 sm:h-4" />
                GitHub
              </a>
              <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer" className="hover:text-foreground transition-colors">
                API Docs
              </a>
              <span className="hidden sm:inline">MIT License</span>
            </div>
          </div>
        </div>
      </footer>
      </div>
    </div>
  );
}
