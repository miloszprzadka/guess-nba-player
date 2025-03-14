'use client';
import { useState } from 'react';

export default function Home() {
  const [guess, setGuess] = useState('');
  const [guessHistory, setGuessHistory] = useState<Array<{name: string, result: any}>>([]);
  const [message, setMessage] = useState('');
  const [gameWin,setGameWin] = useState(false)
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage('');

    const apiUrl = process.env.API || 'http://127.0.0.1:5000/';
    
    try {
      const res = await fetch(apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: guess }),
      });
      
      const rawText = await res.text();
      
      let data = JSON.parse(rawText);

    
      if (!res.ok) {
        console.log("Server error response:", rawText);
        setMessage('Player not found, try again!');
        setGuess('');
        return;
      }
      
      if (data.win === true) {
        setGameWin(true)
        const winMessage = data.message || `You guessed it! The player was ${guess}!`;
        setMessage(`🎉 ${winMessage}`);
        
        if (data.response) {
          console.log(data.response)
          setGuessHistory(prev => [...prev, { name: guess, result: data.response }]);
        }
        
        setGuess('');
        return;
      }
      
      if (data.response) {
        console.log(data.response)
        setGuessHistory(prev => [...prev, { name: guess, result: data.response }]);
      } else {
        setMessage('Player not found, try again!');
      }
      
      setGuess('');
    } catch (error) {
      console.error("Request error:", error);
      setMessage('Error connecting to server. Try again!');
      setGuess('');
    }
  };
  
  const getColorClass = (color: string) => {
    switch (color) {
      case 'green':
        return 'bg-green-500 text-white';
      case 'yellow':
        return 'bg-yellow-400 text-black';
      case 'gray':
        return 'bg-gray-700 text-white';
      default:
        return 'bg-gray-500 text-white';
    }
  };
  
  return (
    <main className='bg-[#FFF2D7]'>
      <div className='flex justify-center items-center'>
        <h1 className="text-4xl font-bold text-[#F98866]">Guess The NBA Player!</h1>
        <img src='/basketball-education.svg' className='w-30 h-30'></img>
      </div>
      <hr className="border-solid border-black border-2 w-[50%] mx-auto mb-5" />
      <div className="min-h-screen flex flex-col">
        <form onSubmit={handleSubmit} className="flex gap-2">
          <input
            type="text"
            value={guess}
            onChange={(e) => setGuess(e.target.value)}
            placeholder={gameWin ? "You won! Come back tomorrow for a new player" : "Enter player name"}            
            className="p-2 rounded text-black bg-white outline-solid w-[50%] mx-auto"
            disabled = {gameWin}
            required
          />
        </form>
        
        {message && (
          <h2 className={`text-2xl m-4 mx-auto ${message.includes('🎉') ? 'text-green-400' : 'text-red-400'}`}>
            {message}
          </h2>
        )}
        
        {/* Show history of guesses */}
        {guessHistory.length > 0 && (
          <div className="w-full max-w-4xl space-y-4 mx-auto">
            
            {guessHistory.map((historyItem, index) => (
              <div key={index} className="m-4">
                <h3 className="text-lg mb-2 font-bold">Guess #{index + 1}: {historyItem.name}</h3>
                
                {historyItem.result && (
                  <div className="overflow-x-auto">
                    <table className="table-auto border-collapse border border-gray-700 w-full ">
                      <thead>
                        <tr>
                          {Object.keys(historyItem.result).map((key) => (
                            <th key={key} className="border border-gray-700">{key}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        <tr>
                          {Object.entries(historyItem.result).map(([key, data]: [string, any]) => {
                            const colorClass = getColorClass(data.color);
                            
                            return (
                              <td
                                key={key}
                                className={`border px-4 py-2 text-center align-middle  ${colorClass}`}
                                style={{
                                  backgroundColor: data.color === 'green' ? '#10B981' : 
                                                data.color === 'yellow' ? '#FBBF24' : 
                                                data.color === 'gray' ? '#4B5563' : '#6B7280',
                                  color: data.color === 'yellow' ? 'black' : 'white'
                                }}>
                                {data.value} {data.hint || ''}
                              </td>
                            );
                          })}
                        </tr>
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </main>
  );
}