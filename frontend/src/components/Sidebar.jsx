import { FiUpload, FiDatabase, FiSettings, FiMenu, FiX } from 'react-icons/fi';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { ScrollArea } from './ui/scroll-area';

export default function Sidebar({ isOpen, setIsOpen, stats }) {
  return (
    <>
      {/* Toggle Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed top-6 left-6 z-50 p-2 bg-card border border-border hover:bg-accent transition-all"
        aria-label="Toggle sidebar"
      >
        {isOpen ? <FiX size={20} /> : <FiMenu size={20} />}
      </button>

      {/* Sidebar */}
      <aside
        className={`fixed left-0 top-0 h-full bg-card border-r-2 border-border transition-transform duration-300 z-40 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        } w-80`}
      >
        {/* Spiral Binding */}
        <div className="spiral-binding">
          <div className="flex flex-col items-center justify-start gap-8 pt-12 pb-12">
            {[...Array(15)].map((_, i) => (
              <div key={i} className="spiral-hole" />
            ))}
          </div>
        </div>

        <ScrollArea className="h-full">
          <div className="p-6 pt-20 pl-20">
            {/* Document Management Section */}
            <Card className="mb-6 bg-background/50 border-border">
              <CardHeader className="pb-3">
                <CardTitle className="text-base font-bold flex items-center gap-2 uppercase tracking-wide">
                  <FiUpload className="text-primary" size={16} />
                  Documents
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-sm text-muted-foreground space-y-2">
                  <div className="p-3 border border-dashed border-border rounded bg-background/30">
                    <p className="text-xs font-medium mb-1">Upload Files</p>
                    <p className="text-xs opacity-70">PDF, TXT, MD, DOCX</p>
                    <p className="text-xs opacity-70">Max 200MB per file</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Stats Section */}
            <Card className="mb-6 bg-background/50 border-border">
              <CardHeader className="pb-3">
                <CardTitle className="text-base font-bold flex items-center gap-2 uppercase tracking-wide">
                  <FiDatabase className="text-primary" size={16} />
                  Knowledge Base
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Document Chunks</span>
                    <Badge variant="secondary" className="font-mono">
                      {stats.totalChunks}
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Settings Section */}
            <Card className="bg-background/50 border-border">
              <CardHeader className="pb-3">
                <CardTitle className="text-base font-bold flex items-center gap-2 uppercase tracking-wide">
                  <FiSettings className="text-primary" size={16} />
                  Configuration
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Reranking</span>
                    <Badge variant="default" className="text-xs">Active</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </ScrollArea>
      </aside>

      {/* Overlay for mobile */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-background/80 backdrop-blur-sm z-30 lg:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}
    </>
  );
}
