import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Loader2, Github } from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";

const quotes = [
  "Every commit tells a story",
  "Each repository holds the seeds of innovation.",
   "Every star shines for a job well done.",
   "Coding fluently in the language of progress.",
   "Building the future, one contribution at a time.",
   "Great minds build better together.",
   "Inspiring a community of like-minded visionaries.",
];

const GithubWrapped = () => {
  const [username, setUsername] = useState('');
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);
  const [error, setError] = useState('');
  const [showNewYear, setShowNewYear] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      const bottom = Math.ceil(window.innerHeight + window.scrollY) >= document.documentElement.scrollHeight;
      if (bottom) {
        setShowNewYear(true);
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const fetchStats = async () => {
    if (!username) {
      setError('Please enter a GitHub username');
      return;
    }

    setLoading(true);
    setError('');
    setData(null);
    
    try {
      const response = await fetch('http://localhost:8000/api/github-wrapped/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username })
      });
      
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const responseData = await response.json();
      if (!responseData?.generated_art) throw new Error('Invalid data format received');
      setData(responseData);
    } catch (err) {
      setError(`Failed to fetch GitHub stats: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 p-4 md:p-8">
      <div className="max-w-3xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl md:text-6xl font-bold text-white mb-4">
            GitHub AI Wrapped 2024
          </h1>
          <p className="text-slate-300 text-lg md:text-xl">
            Scroll through your coding journey
          </p>
        </div>

        <Card className="mb-8">
          <CardContent className="pt-6">
            <div className="flex flex-col md:flex-row gap-4">
              <Input
                placeholder="Enter GitHub username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="flex-grow"
              />
              <Button 
                onClick={fetchStats}
                disabled={loading}
                className="bg-blue-600 hover:bg-blue-700"
              >
                {loading ? (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <Github className="mr-2 h-4 w-4" />
                )}
                Generate Wrapped
              </Button>
            </div>
          </CardContent>
        </Card>

        {error && (
          <Alert variant="destructive" className="mb-8">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {data?.generated_art && (
          <div className="space-y-8">
            {data.generated_art.map((stat, index) => (
              <div key={stat.id} className="flex flex-col items-center">
              <Card key={stat.id} className="w-full transform transition-all hover:scale-102">
                <CardHeader className="bg-slate-800">
                  <CardTitle className="text-white">{stat.stat_name}</CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                  <div className="relative">
                    <img
                      src={stat.image_url}
                      alt={stat.stat_name}
                      className="w-full aspect-square object-cover"
                    />
                    <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-6">
                      <p className="text-white text-2xl font-bold mb-3">
                        {stat.stat_value}
                      </p>
                      <p className="text-slate-200 italic">
                        "{quotes[index % quotes.length]}"
                      </p>
                    </div>
                  </div>

                </CardContent>
              </Card>

            <div className="w-full max-w-4xl text-center mt-8 px-4">
            <p className="text-slate-200 italic text-xl leading-relaxed">
              "{stat.quotation}"
            </p>
            </div>
            </div>
              
            ))}

            {showNewYear && (
              <div className="fixed inset-0 flex items-center justify-center bg-black/70 z-50">
                <div className="text-center animate-bounce">
                  <h2 className="text-6xl font-bold text-white mb-6">
                    🎉 Happy New Year 2025! 🎊
                  </h2>
                  <p className="text-2xl text-white italic">
                  "A new year to write new stories in code. Happy 2025!"
                  </p>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default GithubWrapped;