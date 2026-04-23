import { FiBook } from 'react-icons/fi';

export default function Header() {
  return (
    <header className="border-b-2 border-border bg-card">
      <div className="container mx-auto px-8 py-6">
        <div className="flex items-center gap-4">
          <div className="p-3 bg-primary/10 border-2 border-primary/30">
            <FiBook className="text-primary" size={28} />
          </div>
          <div className="flex flex-col gap-1">
            <h1 className="text-2xl font-bold uppercase tracking-wide">
              Document Intelligence System
            </h1>
            <p className="text-sm text-muted-foreground font-medium">
              Retrieval-Augmented Generation • Knowledge Base Query Interface
            </p>
          </div>
        </div>
      </div>
    </header>
  );
}
