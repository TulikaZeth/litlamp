import { FiPlusCircle } from 'react-icons/fi';
import { Button } from './ui/button';
import { Card } from './ui/card';
import { ScrollArea } from './ui/scroll-area';

export default function StudioPanel() {
  const studioOptions = [
    { icon: '🎧', label: 'Audio Overview', color: 'from-blue-500 to-purple-500' },
    { icon: '📹', label: 'Video Overview', color: 'from-green-500 to-teal-500' },
    { icon: '📊', label: 'Reports', color: 'from-orange-500 to-red-500' },
    { icon: '⚡', label: 'Flashcards', color: 'from-yellow-500 to-orange-500' },
    { icon: '📈', label: 'Infographic', color: 'from-pink-500 to-purple-500' },
    { icon: '🎯', label: 'Quiz', color: 'from-indigo-500 to-blue-500' },
    { icon: '🎨', label: 'Slide Deck', color: 'from-teal-500 to-green-500' },
    { icon: '🗺️', label: 'Mind Map', color: 'from-purple-500 to-pink-500' },
  ];

  return (
    <div className="w-96 bg-card border-l border-border flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-border">
        <h2 className="text-lg font-semibold">Studio</h2>
      </div>

      {/* Content */}
      <ScrollArea className="flex-1">
        <div className="p-4">
          {/* Featured */}
          <div className="mb-6">
            <Card className="bg-gradient-to-br from-purple-600 to-blue-600 border-0 p-4">
              <div className="text-white space-y-2">
                <h3 className="font-semibold">
                  Create an Audio Overview in: हिंदी, বাংলা, తెలుగు, ગુજરાતી, ਪੰਜਾਬੀ, മലയാളം, தமிழ், ಕನ್ನಡ
                </h3>
              </div>
            </Card>
          </div>

          {/* Studio Options Grid */}
          <div className="grid grid-cols-2 gap-3">
            {studioOptions.map((option, idx) => (
              <Card
                key={idx}
                className="p-4 cursor-pointer hover:bg-accent transition-colors bg-card border-border group"
              >
                <div className="flex flex-col items-center gap-2 text-center">
                  <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${option.color} flex items-center justify-center text-2xl`}>
                    {option.icon}
                  </div>
                  <span className="text-sm font-medium">{option.label}</span>
                </div>
              </Card>
            ))}
          </div>

          {/* Output Info */}
          <div className="mt-6 p-4 bg-background rounded-lg border border-border text-center">
            <div className="mb-2">
              <span className="text-4xl">🎨</span>
            </div>
            <p className="text-sm text-primary font-medium mb-2">Studio output will be saved here</p>
            <p className="text-xs text-muted-foreground">
              After adding sources, click to add Audio Overview, Study Guide, Mind Map, and more!
            </p>
          </div>
        </div>
      </ScrollArea>

      {/* Footer Button */}
      <div className="p-4 border-t border-border">
        <Button className="w-full gap-2 bg-white text-black hover:bg-gray-200">
          <FiPlusCircle size={16} />
          Add note
        </Button>
      </div>
    </div>
  );
}
