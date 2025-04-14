import React, { useState, useCallback } from 'react';
import { data, useNavigate } from 'react-router-dom';
import '../styles.css';
import { viewTransition } from '../utils';
import Checkbox from './Checkbox';
import { useAppStore } from './appStore';
const HomePage: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const navigate = useNavigate();
  const { state, dispatch } = useAppStore();

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      viewTransition(() => navigate(`/results?q=${encodeURIComponent(searchQuery)}`), true);
    }
  };

  const handleLTRChange = useCallback((value: boolean, ev: React.MouseEvent<HTMLDivElement>) => {
    ev.stopPropagation();
    dispatch({
      type: 'setLTR',
      data: value
    })
  }, [dispatch]);

  const handleLogoClick = () => {
    window.open('https://www.google.com/search?q=Pantheon+(TV+series)&oq=pantheon&gs_lcrp=EgZjaHJvbWUqDggDEEUYJxg7GIAEGIoFMg8IABBFGDkYgwEYsQMYgAQyEwgBEC4YgwEYrwEYxwEYsQMYgAQyCggCEC4YsQMYgAQyDggDEEUYJxg7GIAEGIoFMgYIBBBFGDsyBggFEEUYPDIGCAYQRRg8MgYIBxBFGDzSAQg0NDE1ajBqN6gCALACAA&sourceid=chrome&ie=UTF-8', '_blank');
  };

  return (
    <div className="home-page container container-md">
      <div className="flex-center">
        <div className="card">
          <div className="team-info">
            Powered by <span>Team #69</span> with ❤️
            <div className="team-popup">
              <div className='team-popup-title'><img src='./assets/ai-army-logo.jpeg' alt='AI Army Logo' width={28}></img><b>AI Army</b></div>
              <div className='team-popup-content'>
                <div>
                  <div><img src='./assets/avatar-xiao.webp' alt='Xiao Yang' width={28}></img>Xiao Yang <i>@_aotake_</i></div>
                  <p>"Curiosity is the key."</p>
                </div>
                <div>
                  <div><img src='./assets/avatar-lucas.webp' alt='Lucas Ong' width={28}></img>Lucas Ong <i>@shr00ms007</i></div>
                  <p>"I'm not a fan of the AI Army."</p>
                </div>
                <div>
                  <div><img src='./assets/avatar-gracie.webp' alt='Mary Schafer' width={28}></img>Mary Schafer <i>@juicyjuice3586</i></div>
                  <p>"Not available."</p>
                </div>
                <div>
                  <div><img src='./assets/avatar-jason.gif' alt='Jason Tan' width={28}></img>Jason Tan <i>@kuugo25</i></div>
                  <p>"KYS"</p>
                </div>
              </div>

            </div>
          </div>
          <h1 className="title" onClick={handleLogoClick}>
            <img src="./assets/pantheon-logo.png" alt="Pantheon Logo" width={180} />
          </h1>
          <p className="subtitle"></p>
          <form onSubmit={handleSearch} className="form">
            <div className='search-input-container'>
              <input
                autoFocus
                type="text"
                className="search-input"
                placeholder="Find your next favorite game..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <div className='search-button-container'>
              <div className='search-button-icon-container'>
                <span className='search-button-icon'>!</span>
                <span className='search-button-text'>Kaggle<br/>40985 items</span>
              </div>
              <button
                type="submit"
                className="main-button"
                disabled={!searchQuery.trim()}
              >
                SEARCH
              </button>
            </div>
            <div className='ltr-switcher' onClick={() => { dispatch({type: 'toggleLTR'}) }}>
              <Checkbox checked={state.useLTR} onChange={handleLTRChange}></Checkbox>
              <div className='switch-text'>LTR: {state.useLTR ? 'ON': 'OFF'}</div>
              <p>// Use LambdaMART instead of manually assigned weights for ranking</p>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default HomePage; 