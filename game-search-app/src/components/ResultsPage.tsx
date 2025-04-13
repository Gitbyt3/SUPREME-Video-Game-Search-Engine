import React, { useEffect, useRef, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import '../styles.css';
import { GenreIcon, type Genre } from './GenreIcon';
import LoadingAnimation from './LoadingAnimation';
import Typewriter from './Typewriter';
import { viewTransition } from '../utils';
import { query as apiQuery, recordCtr } from '../utils/api';

interface Game {
  id: number;
  title: string;
  description: string;
  summary?: string;
  genres: Genre[];
  releaseYear: number;
  platforms: string[];
  rating: number;
  developers: string[];
  plays: string;
  bm25Score?: number;
  bm25Scores?: number[];
  sbertScore?: number;
  ctr?: number;
}

// Mock data
// const mockGames: Game[] = [
//   {
//     id: 1,
//     title: "The Legend of Zelda: Breath of the Wild",
//     description: `The Sporting News Baseball doesn't feature a Major League license, but does feature the MLBPA license, meaning that it features some of the best players of the time, such as Ken Griffey Jr., Daryl Strawberry and John Smoltz, to name a few. There are only three stadiums to pick from; two are generic but the other is the baseball field from the movie Field of Dreams.
// There are several modes such as exhibition games, All-Star Game, the Home Run Derby, and a pennant race. The gameplay is similar to other baseball games, certain buttons to swing the bat and bunting or selecting pitches.`,
//     genres: ["Turn Based Strategy", "Tactical"],
//     releaseYear: 2017,
//     platforms: ["Nintendo Switch", "PlayStation 4", "Xbox One"],
//     rating: 9.8,
//     developers: ["Nintendo"],
//     plays: "4.5k"
//   },
//   {
//     id: 2,
//     title: "Red Dead Redemption 2",
//     description: "An epic tale of honor and loyalty in America's heartland.",
//     genres: ["Tactical", "Adventure"],
//     releaseYear: 2018,
//     platforms: ["Nintendo Switch", "PlayStation 4", "Xbox One"],
//     rating: 9.7,
//     developers: ["Rockstar Games"],
//     plays: "1.5k"
//   },
//   {
//     id: 3,
//     title: "The Witcher 3: Wild Hunt",
//     description: "A story-driven open world RPG set in a visually stunning fantasy universe.",
//     genres: ["Visual Novel", "Adventure"],
//     releaseYear: 2015,
//     rating: 9.6,
//     platforms: ["Nintendo Switch", "PlayStation 4", "Xbox One"],
//     developers: ["CD Projekt Red"],
//     plays: "1.2k"
//   },
//   {
//     id: 4,
//     title: "Super Mario Odyssey",
//     description: "A platformer that features a large open world and a focus on exploration.",
//     genres: ["Shooter", "Adventure"],
//     releaseYear: 2017,
//     rating: 9.5,
//     platforms: ["Nintendo Switch", "PlayStation 4", "Xbox One"],
//     developers: ["Nintendo"],
//     plays: "1.2k"
//   },
//   {
//     id: 5,
//     title: "The Last of Us Part II",
//     description: "A story-driven action-adventure game set in a post-apocalyptic world.",
//     genres: ["Real Time Strategy", "RPG", "Adventure"],
//     releaseYear: 2020,
//     rating: 9.4,
//     platforms: ["Nintendo Switch", "PlayStation 4", "Xbox One"],
//     developers: ["Naughty Dog"],
//     plays: "12.2k"
//   },
//   {
//     id: 6,
//     title: "The Last of Us Part II",
//     description: "A story-driven action-adventure game set in a post-apocalyptic world.",
//     genres: ["Racing", "Adventure"],
//     releaseYear: 2020,
//     rating: 9.4,
//     platforms: ["Nintendo Switch", "PlayStation 4", "Xbox One"],
//     developers: ["Naughty Dog"],
//     plays: "1.2k"
//   },
//   {
//     id: 7,
//     title: "The Last of Us Part II",
//     description: "A story-driven action-adventure game set in a post-apocalyptic world.",
//     genres: ["RPG", "Adventure"],
//     releaseYear: 2020,
//     rating: 9.4,
//     platforms: ["Nintendo Switch", "PlayStation 4", "Xbox One"],
//     developers: ["Naughty Dog"],
//     plays: "5.2k"
//   },
//   {
//     id: 8,
//     title: "The Last of Us Part II",
//     description: "A story-driven action-adventure game set in a post-apocalyptic world.",
//     genres: ["Quiz/Trivia", "Adventure"],
//     releaseYear: 2020,
//     rating: 9.4,
//     platforms: ["Nintendo Switch", "PlayStation 4", "Xbox One"],
//     developers: ["Naughty Dog"],
//     plays: "1.2k"
//   },
//   {
//     id: 9,
//     title: "The Last of Us Part II",
//     description: "A story-driven action-adventure game set in a post-apocalyptic world.",
//     genres: ["Puzzle", "Adventure"],
//     releaseYear: 2020,
//     rating: 9.4,
//     platforms: ["Nintendo Switch", "PlayStation 4", "Xbox One"],
//     developers: ["Naughty Dog"],
//     plays: "1.2k"
//   },
//   {
//     id: 10,
//     title: "The Last of Us Part II",
//     description: "A story-driven action-adventure game set in a post-apocalyptic world.",
//     genres: ["Point-and-Click", "Adventure"],
//     releaseYear: 2020,
//     rating: 9.4,
//     platforms: ["Nintendo Switch", "PlayStation 4", "Xbox One"],
//     developers: ["Naughty Dog", "Rockstar Games"],
//     plays: "1.2k"
//   }
// ];

const ResultsPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const [games, setGames] = useState<Game[]>([]);
  const navigate = useNavigate();
  const query = searchParams.get('q') || '';
  const [selectedGame, setSelectedGame] = useState<Game | null>(null);
  const [searchQuery, setSearchQuery] = useState<string>(query);
  const [isLoading, setIsLoading] = useState(true);
  const [lastResponseTime, setLastResponseTime] = useState<string>('');
  let lastQuery = useRef<string>('');

  useEffect(() => {
    console.log(lastQuery.current, query);
    if (lastQuery.current === query) {
      return;
    }
    lastQuery.current = query;
    const fetchData = async() => {
      const result = await apiQuery(query || '');
      console.log(result);
      setGames(result);
      setIsLoading(false);
      setLastResponseTime(((Date.now() - now) / 1000).toFixed(2))
    }
    setSearchQuery(query || '');
    setIsLoading(true);

    const now = Date.now();
    fetchData();

    return () => {
      // clean up
    };
  }, [query]);

  const handleSearch = (e: React.FormEvent, query: string) => {
    e.preventDefault();
    navigate(`/results?q=${encodeURIComponent(query)}`);
  };

  const handleGameClick = (game: Game) => {
    setSelectedGame(game);
    recordCtr(game.id);
  };

  const closeModal = () => {
    setSelectedGame(null);
  };

  return (
    <div className="container results-page">
      <div className="search-bar">
        <div className='search-bar-background'></div>
        <img onClick={() => viewTransition(() => navigate('/'))} src="./assets/pantheon-logo.png" alt="Pantheon Logo" width={120} />
        <div className="search-input-container">
          <input type="text" className="search-input" placeholder="Search for games..." value={searchQuery} onKeyDown={(e) => {
            if (e.key === 'Enter') {
              handleSearch(e, searchQuery);
            }
          }} onChange={(e) => setSearchQuery(e.target.value)} />
          <button className="button" onClick={(e) => handleSearch(e, searchQuery)}>SEARCH</button>
        </div>
      </div>
      {isLoading ? (
        <LoadingAnimation />
      ) : (
        <>
          <h1 className="title">
            <Typewriter text={`Search results for "${query}" in ${lastResponseTime}`} />
          </h1>
          <div className="results-grid">
            {games.map((game, index) => (
              <div
              key={game.id}
              className={["game-card", selectedGame?.id === game.id ? "selected" : ""].join(" ")}
              style={{ '--animation-order': index
               } as React.CSSProperties}
              onClick={() => handleGameClick(game)}
            >
              <div className="game-image">
                <GenreIcon genre={game.genres[0]} size={60} />
              </div>
              <div className="game-content">
                <h2 className="game-title">{game.title}<sup>{game.releaseYear}</sup></h2>
                <p className="game-meta">
                  <div className="game-genre">
                    <i className="fa-solid fa-gamepad"></i>
                    {game.genres.join(' • ')}
                  </div>
                  <div className='game-platform'>
                    <i className="fa-solid fa-desktop"></i>
                    {game.platforms.join(' • ')}
                  </div>
                  <div className='game-developer'>
                    <i className="fa-solid fa-ghost"></i>
                    {game.developers.join(' • ')}
                  </div>
                </p>
                <div className="game-meta-numerical">
                  <div className="game-rating" title="Rating">
                    <img src="./assets/star.png" alt="Rating" width={16} />
                    <b>{game.rating}</b>/10
                  </div>
                  <div className="game-players" title="Players">
                    <b>{game.plays}</b>
                    <span>Players</span>
                  </div>
                </div>
              </div>
              <div className="debug-info">
                <div className="debug-info-title">Debug Info</div>
                <div>DOC ID: {game.id}</div>
                <div>BM25 Score: {game.bm25Score ?? '-'}</div>
                <div>BM25 Details: {game.bm25Scores?.map(item => +item.toFixed(3)).join(',')}</div>
                <div>SBERT Score: {+(game.sbertScore?.toFixed(7) || 0)}</div>
                <div>CTR: {game.ctr}</div>
              </div>
            </div>
          ))}
          </div>
        </>
      )}

      {selectedGame && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="game-detail-modal" onClick={e => e.stopPropagation()}>
            <button className="close-button" onClick={closeModal}>×</button>
            <div className="modal-content">
              <div className="modal-header">
                <h2 className="modal-title"><Typewriter text={selectedGame.title} /></h2>
                <div className="modal-meta">
                  <span className="modal-year">{selectedGame.releaseYear}</span>
                  <span className="modal-rating">
                    <img src="./assets/star.png" alt="Rating" width={16} />
                    <b>{selectedGame.rating}</b>/10
                  </span>
                </div>
              </div>
              <div className="modal-body">
                <p className="modal-description">{selectedGame.summary}</p>
                <div className="modal-details">
                  <div className="modal-genre">
                    <i className="fa-solid fa-gamepad"></i>
                    <span>{selectedGame.genres.join(' • ')}</span>
                  </div>
                  <div className="modal-platform">
                    <i className="fa-solid fa-desktop"></i>
                    <span>{selectedGame.platforms.join(' • ')}</span>
                  </div>
                  <div className="modal-developer">
                    <i className="fa-solid fa-ghost"></i>
                    <span>{selectedGame.developers.join(' • ')}</span>
                  </div>
                  <div className="modal-players">
                    <i className="fa-solid fa-users"></i>
                    <span>{selectedGame.plays} Players</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ResultsPage; 