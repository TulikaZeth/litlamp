import { Menu, Share2, BarChart2, Settings, MoreVertical, BookOpen } from 'lucide-react';
import { Button } from './ui/button';
import { Badge } from './ui/badge';

export default function NotebookHeader({ isHealthy, stats }) {

  
  return (
    <header className="bg-card border-b border-border px-2 sm:px-4 py-2 sm:py-3">
      <div className="flex items-center justify-between">
        {/* Left side */}
        <div className="flex items-center gap-1 sm:gap-3">
          <Button variant="ghost" size="icon" className="hidden sm:flex">
            <Menu size={20} />
          </Button>
          <div className="flex items-center gap-1 sm:gap-2">
            <div className="w-7 h-7 sm:w-8 sm:h-8 bg-card border-2 border-primary rounded-lg flex items-center justify-center">
              <BookOpen size={16} className="text-primary sm:w-5 sm:h-5" />
            </div>
            <span className="font-semibold text-sm sm:text-base hidden xs:inline">RAG Bot Notebook</span>
            <span className="font-semibold text-sm xs:hidden">RAG Bot</span>
            {stats && (
              <Badge variant="outline" className="text-xs font-mono hidden sm:inline-flex">
                {stats.documents || stats.total_chunks || 0} chunks
              </Badge>
            )}
          </div>
        </div>

        {/* Right side */}
        <div className="flex items-center gap-1 sm:gap-2">
          <div className="flex items-center gap-1 sm:gap-2 mr-1 sm:mr-2">
            <div className={`w-2 h-2 rounded-full ${isHealthy ? 'bg-green-500' : 'bg-red-500'}`} />
            <span className="text-xs text-muted-foreground hidden md:inline">
              {isHealthy ? 'Connected' : 'Disconnected'}
            </span>
          </div>
          <Button variant="ghost" size="sm" className="gap-2 hidden lg:flex">
            <BarChart2 size={16} />
            Analytics
          </Button>
     
          <Button variant="ghost" size="sm" className="gap-2 hidden md:flex">
            <Settings size={16} />
            Settings
          </Button>
          <div className="flex items-center gap-1 ml-1 sm:ml-2">
            <span className="text-xs bg-primary/20 text-primary px-1.5 sm:px-2 py-1 rounded hidden sm:inline">PRO</span>
            <Button variant="ghost" size="icon" className="hidden sm:flex">
              <MoreVertical size={16} />
            </Button>
            <Button variant="ghost" size="icon" className="w-7 h-7 sm:w-8 sm:h-8 rounded-full bg-card border-2 border-primary text-foreground text-xs sm:text-sm">
              G
            </Button>
          </div>
        </div>
      </div>
    </header>
  );
}
