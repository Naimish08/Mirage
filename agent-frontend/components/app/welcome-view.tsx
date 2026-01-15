import { Button } from '@/components/livekit/button';
import { usePersona } from '@/components/app/persona-context';
import { cn } from '@/lib/utils';
import { Check } from '@phosphor-icons/react/dist/ssr';
import { useAuth } from '@/contexts/auth-context';
import { SignOut } from '@phosphor-icons/react/dist/ssr';

interface WelcomeViewProps {
  startButtonText: string;
  onStartCall: () => void;
}


export const WelcomeView = ({
  startButtonText,
  onStartCall,
  ref,
}: React.ComponentProps<'div'> & WelcomeViewProps) => {
  const { currentPersona, setPersona, personas } = usePersona();
  const { signOut } = useAuth();

  return (
    <div ref={ref} className="flex min-h-full flex-col items-center justify-center p-4">
      {/* Logout Button */}
      <button
        onClick={signOut}
        className="fixed top-6 right-6 z-50 flex items-center gap-2 px-4 py-2 bg-white/5 hover:bg-white/10 border border-white/10 hover:border-white/20 rounded-lg text-white/70 hover:text-white transition-all duration-200"
        title="Sign Out"
      >
        <SignOut weight="bold" className="size-5" />
        <span className="text-sm font-medium">Logout</span>
      </button>

      <section className="bg-background flex flex-col items-center justify-center text-center max-w-4xl mx-auto">
        <h2 className="mb-2 text-2xl font-bold tracking-tight">Choose Your Assistant</h2>
        <p className="text-muted-foreground mb-8 max-w-prose text-sm">
          Select an avatar to customize your experience.
        </p>

        {/* Persona Selection Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full mb-8">
          {personas.map((persona) => {
            const isSelected = currentPersona.id === persona.id;
            return (
              <div
                key={persona.id}
                onClick={() => setPersona(persona)}
                className={cn(
                  "relative group cursor-pointer overflow-hidden rounded-xl border-2 transition-all duration-200 hover:border-primary/50",
                  isSelected ? "border-primary bg-primary/5 ring-4 ring-primary/10" : "border-border bg-card"
                )}
              >
                <div className="aspect-video w-full overflow-hidden">
                  <img
                    src={persona.image}
                    alt={persona.name}
                    className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
                  />
                  {/* Overlay for theme preview */}
                  <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-60" />
                </div>

                <div className="absolute bottom-0 left-0 right-0 p-4 text-left">
                  <div className="flex items-center justify-between">
                    <h3 className="text-white font-semibold text-lg">{persona.name}</h3>
                    {isSelected && (
                      <div className="bg-primary rounded-full p-1 text-primary-foreground">
                        <Check weight="bold" className="size-4" />
                      </div>
                    )}
                  </div>
                  <p className="text-white/80 text-xs mt-1">{persona.description}</p>
                </div>
              </div>
            );
          })}
        </div>

        <Button
          variant="primary"
          size="lg"
          onClick={onStartCall}
          className="w-full md:w-64 font-mono text-lg py-6 shadow-lg shadow-primary/20 hover:shadow-primary/40 transition-shadow"
        >
          {startButtonText}
        </Button>
      </section>

      <div className="fixed bottom-5 left-0 flex w-full items-center justify-center pointer-events-none">
        <p className="text-muted-foreground/50 text-xs">
          Powered by LiveKit & Gemini
        </p>
      </div>
    </div>
  );
};

