import React, { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { authService } from '../services/authService'
import axiosInstance from '../services/axiosConfig'

export default function ProfileSettings() {
  const navigate = useNavigate()
  const userInfo = authService.getUserInfo()

  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [languageSearch, setLanguageSearch] = useState('')
  const [showLanguageDropdown, setShowLanguageDropdown] = useState(false)
  const [actorSearch, setActorSearch] = useState('')
  const [showActorDropdown, setShowActorDropdown] = useState(false)

  const [profile, setProfile] = useState({
    preferences: '',
    favorite_genres: [],
    disliked_genres: [],
    favorite_actors: [],
    watch_style: '',
    mood_preference: '',
    recently_watched: [],
    watching_with: 'solo',
    time_available: '2-3 hours',
    language_preference: ''
  })

  // Genre options
  const genreOptions = [
    'action',
    'anime',
    'thriller',
    'sci-fi',
    'comedy',
    'romance',
    'drama',
    'horror',
    'mystery',
    'fantasy',
    'documentary',
    'martial arts',
    'adventure',
    'crime',
    'musical',
    'western',
    'war',
    'biography',
    'animation'
  ]

  // Country/Language options from Netflix dataset
  const countryOptions = [
    'United States',
    'United Kingdom',
    'Canada',
    'Australia',
    'France',
    'Germany',
    'Japan',
    'South Korea',
    'China',
    'India',
    'Spain',
    'Italy',
    'Mexico',
    'Brazil',
    'Argentina',
    'Netherlands',
    'Belgium',
    'Sweden',
    'Norway',
    'Denmark',
    'Finland',
    'Switzerland',
    'Austria',
    'Ireland',
    'New Zealand',
    'South Africa',
    'Nigeria',
    'Egypt',
    'Turkey',
    'Russia',
    'Poland',
    'Czech Republic',
    'Hong Kong',
    'Taiwan',
    'Singapore',
    'Thailand',
    'Indonesia',
    'Malaysia',
    'Philippines',
    'Vietnam',
    'Pakistan',
    'Bangladesh',
    'Israel',
    'Lebanon',
    'Saudi Arabia',
    'United Arab Emirates',
    'Qatar',
    'Kuwait',
    'Jordan',
    'Iran',
    'Iraq',
    'Syria',
    'Palestine',
    'Colombia',
    'Chile',
    'Peru',
    'Uruguay',
    'Venezuela',
    'Portugal',
    'Greece',
    'Romania',
    'Bulgaria',
    'Hungary',
    'Croatia',
    'Serbia',
    'Ukraine',
    'Ghana',
    'Kenya',
    'Ethiopia',
    'Cameroon',
    'Senegal',
    'Zimbabwe',
    'Mozambique',
    'Angola',
    'Namibia',
    'Mauritius',
    'Iceland',
    'Luxembourg',
    'Malta',
    'Cyprus',
    'Liechtenstein',
    'Monaco',
    'Vatican City'
  ].sort()

  // Mood options
  const moodOptions = [
    { value: 'fast-paced', label: 'Fast-paced & Adrenaline', emoji: '⚡' },
    { value: 'uplifting', label: 'Uplifting & Heartwarming', emoji: '🌟' },
    { value: 'relaxing', label: 'Relaxing & Calm', emoji: '😌' },
    { value: 'intense', label: 'Intense & Gripping', emoji: '🔥' },
    { value: 'emotional', label: 'Emotional & Deep', emoji: '💔' },
    { value: 'funny', label: 'Funny & Light-hearted', emoji: '😂' },
    { value: 'inspiring', label: 'Inspiring & Motivational', emoji: '💪' },
    { value: 'dark', label: 'Dark & Mysterious', emoji: '🌑' },
    { value: 'romantic', label: 'Romantic & Sweet', emoji: '💕' },
    { value: 'thrilling', label: 'Thrilling & Suspenseful', emoji: '😱' },
    { value: 'thought-provoking', label: 'Thought-provoking', emoji: '🤔' },
    { value: 'nostalgic', label: 'Nostalgic & Classic', emoji: '📼' }
  ]

  // Actor/Actress options
  const actorOptions = [
    'Tom Cruise',
    'Keanu Reeves',
    'Leonardo DiCaprio',
    'Denzel Washington',
    'Samuel L. Jackson',
    'Robert De Niro',
    'Brad Pitt',
    'Johnny Depp',
    'Harrison Ford',
    'Bruce Willis',
    'Will Smith',
    'Matt Damon',
    'Christian Bale',
    'Hugh Jackman',
    'Ryan Reynolds',
    'Chris Evans',
    'Chris Hemsworth',
    'Mark Wahlberg',
    'Dwayne Johnson',
    'Vin Diesel',
    'Scarlett Johansson',
    'Jennifer Lawrence',
    'Angelina Jolie',
    'Nicole Kidman',
    'Meryl Streep',
    'Emma Stone',
    'Charlize Theron',
    'Natalie Portman',
    'Anne Hathaway',
    'Amy Adams',
    'Margot Robbie',
    'Gal Gadot',
    'Zendaya',
    'Florence Pugh',
    'Anya Taylor-Joy',
    'Ama Qamata',
    'Khosi Ngema',
    'Gail Mabalane',
    'Thabang Molaba',
    'Dillon Windvogel',
    'Natasha Thahane',
    'Arno Greeff',
    'Xolile Tshabalala',
    'Getmore Sithole',
    'Cindy Mahlangu',
    'Sami Bouajila',
    'Tracy Gotoas',
    'Samuel Jouy',
    'Nabiha Akkari',
    'Sofia Lesaffre',
    'Mayur More',
    'Jitendra Kumar',
    'Ranjan Raj',
    'Alam Khan',
    'Ahsaas Channa',
    'Kate Siegel',
    'Zach Gilford',
    'Hamish Linklater',
    'Henry Thomas',
    'Kristin Lehman',
    'Vanessa Hudgens',
    'Kimiko Glenn',
    'James Marsden',
    'Sofia Carson',
    'Liza Koshy',
    'Ken Jeong',
    'Elizabeth Perkins',
    'Jane Krakowski',
    'Michael McKean',
    'Phil LaMarr',
    'Melissa McCarthy',
    "Chris O'Dowd",
    'Kevin Kline',
    'Timothy Olyphant',
    'Daveed Diggs',
    'Luna Wedler',
    'Jannis Niewöhner',
    'Milan Peschel',
    'Edin Hasanović',
    'Anna Fialová',
    'Klara Castanho',
    'Lucca Picon',
    'Júlia Gomes',
    'Marcus Bessa',
    'Kiria Malheiros',
    'Logan Browning',
    'Brandon P. Bell',
    'DeRon Horton',
    'Antoinette Robertson',
    'Asa Butterfield',
    'Gillian Anderson',
    'Ncuti Gatwa',
    'Emma Mackey',
    'Connor Swindells',
    'Lee Jung-jae',
    'Park Hae-soo',
    'Wi Ha-jun',
    'Oh Young-soo',
    'Jung Ho-yeon',
    'Roy Scheider',
    'Robert Shaw',
    'Richard Dreyfuss',
    'Lorraine Gary',
    'Murray Hamilton',
    'Jack Black',
    'Dustin Hoffman',
    'Ian McShane',
    'Seth Rogen',
    'Lucy Liu',
    'Jackie Chan',
    'David Cross',
    'Michelle Yeoh',
    'Gary Oldman',
    'Michael Caine',
    'Tom Hanks',
    'Morgan Freeman',
    'Clint Eastwood',
    'Al Pacino',
    'Sylvester Stallone',
    'Arnold Schwarzenegger',
    'Jason Statham',
    'Jackie Shroff',
    'Amitabh Bachchan',
    'Shah Rukh Khan',
    'Aamir Khan',
    'Salman Khan',
    'Akshay Kumar',
    'Hrithik Roshan',
    'Ranveer Singh',
    'Ranbir Kapoor',
    'Deepika Padukone',
    'Priyanka Chopra',
    'Alia Bhatt',
    'Katrina Kaif',
    'Kareena Kapoor',
    'Aishwarya Rai Bachchan',
    'Madhuri Dixit',
    'Kajol',
    'Vidya Balan',
    'Taapsee Pannu',
    'Kangana Ranaut',
    'Sanjay Dutt',
    'Vijay Sethupathi',
    'Suriya',
    'Park Seo-joon',
    'Song Joong-ki',
    'Lee Min-ho',
    'Hyun Bin',
    'Gong Yoo',
    'IU (Lee Ji-eun)',
    'Bae Suzy',
    'Jun Ji-hyun',
    'Song Hye-kyo',
    'Park Shin-hye',
    'Kim Soo-hyun',
    'Park Bo-gum',
    'Ji Chang-wook',
    'Lee Jong-suk',
    'Nam Joo-hyuk',
    'Robert Downey Jr.',
    'Chris Pratt',
    'Benedict Cumberbatch',
    'Tom Holland',
    'Paul Rudd',
    'Chadwick Boseman',
    'Michael B. Jordan',
    'Idris Elba',
    'Mahershala Ali',
    'Daniel Kaluuya',
    "Lupita Nyong'o",
    'Viola Davis',
    'Octavia Spencer',
    'Taraji P. Henson',
    'Halle Berry',
    'Jamie Foxx',
    'Eddie Murphy',
    'Kevin Hart',
    'Dave Chappelle',
    'Chris Rock',
    'Adam Sandler',
    'Jim Carrey',
    'Ben Stiller',
    'Owen Wilson',
    'Vince Vaughn',
    'Jennifer Aniston',
    'Reese Witherspoon',
    'Sandra Bullock',
    'Julia Roberts',
    'Cameron Diaz',
    'Kate Winslet',
    'Cate Blanchett',
    'Tilda Swinton',
    'Helen Mirren',
    'Judi Dench',
    'Maggie Smith',
    'Emma Thompson',
    'Rachel Weisz',
    'Keira Knightley',
    'Emily Blunt',
    'Daniel Craig',
    'Pierce Brosnan',
    'Sean Connery',
    'Roger Moore',
    'Timothy Dalton',
    'Jason Momoa',
    'Henry Cavill',
    'Ben Affleck',
    'Gal Gadot',
    'Ezra Miller',
    'Zachary Levi',
    'Michael Keaton',
    'Val Kilmer',
    'George Clooney',
    'Adam West',
    'Ryan Gosling',
    'Jake Gyllenhaal',
    'Joseph Gordon-Levitt',
    'Andrew Garfield',
    'Timothée Chalamet',
    'Oscar Isaac',
    'Adam Driver',
    'John Boyega',
    'Daisy Ridley',
    'Mark Hamill',
    'Carrie Fisher',
    'Billy Dee Williams',
    'Ewan McGregor',
    'Liam Neeson',
    'Natalie Portman',
    'Hayden Christensen',
    'Samuel L. Jackson',
    'Alec Guinness',
    'Peter Cushing',
    'Christopher Lee',
    'Elijah Wood',
    'Ian McKellen',
    'Viggo Mortensen',
    'Orlando Bloom',
    'Sean Astin',
    'Andy Serkis',
    'Liv Tyler',
    'Cate Blanchett',
    'Hugo Weaving',
    'Karl Urban'
  ].sort()

  // Filter countries based on search
  const filteredCountries = countryOptions.filter((country) =>
    country.toLowerCase().includes(languageSearch.toLowerCase())
  )

  // Filter actors based on search
  const filteredActors = actorOptions.filter((actor) => actor.toLowerCase().includes(actorSearch.toLowerCase()))

  // Load profile function
  const loadProfile = useCallback(async () => {
    try {
      setLoading(true)
      const response = await axiosInstance.get(`/api/auth/profile/${userInfo.id}`)
      if (response.data.profile) {
        setProfile({
          preferences: response.data.profile.preferences || '',
          favorite_genres: response.data.profile.favorite_genres || [],
          disliked_genres: response.data.profile.disliked_genres || [],
          favorite_actors: response.data.profile.favorite_actors || [],
          watch_style: response.data.profile.watch_style || '',
          mood_preference: response.data.profile.mood_preference || '',
          recently_watched: response.data.profile.recently_watched || [],
          watching_with: response.data.profile.watching_with || 'solo',
          time_available: response.data.profile.time_available || '2-3 hours',
          language_preference: response.data.profile.language_preference || ''
        })
      }
    } catch (err) {
      console.error('Load profile error:', err)
      setError('Failed to load profile')
    } finally {
      setLoading(false)
    }
  }, [userInfo.id])

  // Load profile on mount
  useEffect(() => {
    loadProfile()
  }, [loadProfile])

  const toggleCountry = (country) => {
    const currentCountries = profile.language_preference
      .split(',')
      .map((c) => c.trim())
      .filter(Boolean)
    if (currentCountries.includes(country)) {
      const updated = currentCountries.filter((c) => c !== country)
      setProfile({ ...profile, language_preference: updated.join(', ') })
    } else {
      const updated = [...currentCountries, country]
      setProfile({ ...profile, language_preference: updated.join(', ') })
    }
  }

  const isCountrySelected = (country) => {
    const currentCountries = profile.language_preference
      .split(',')
      .map((c) => c.trim())
      .filter(Boolean)
    return currentCountries.includes(country)
  }

  const toggleActor = (actor) => {
    if (profile.favorite_actors.includes(actor)) {
      setProfile({
        ...profile,
        favorite_actors: profile.favorite_actors.filter((a) => a !== actor)
      })
    } else {
      setProfile({
        ...profile,
        favorite_actors: [...profile.favorite_actors, actor]
      })
    }
  }

  const isActorSelected = (actor) => {
    return profile.favorite_actors.includes(actor)
  }

  const handleSave = async () => {
    try {
      setSaving(true)
      setMessage('')
      setError('')

      await axiosInstance.put(`/api/auth/profile/${userInfo.id}`, profile)

      setMessage('Profile updated successfully! Redirecting to home...')

      // Redirect to home page after 1.5 seconds
      setTimeout(() => {
        navigate('/')
      }, 1500)
    } catch (err) {
      console.error('Save profile error:', err)
      setError('Failed to save profile')
    } finally {
      setSaving(false)
    }
  }

  const toggleGenre = (genre, type) => {
    const key = type === 'favorite' ? 'favorite_genres' : 'disliked_genres'
    setProfile((prev) => {
      const genres = prev[key]
      if (genres.includes(genre)) {
        return { ...prev, [key]: genres.filter((g) => g !== genre) }
      } else {
        return { ...prev, [key]: [...genres, genre] }
      }
    })
  }

  const addToList = (field, value) => {
    if (!value.trim()) return
    setProfile((prev) => ({
      ...prev,
      [field]: [...prev[field], value.trim()]
    }))
  }

  const removeFromList = (field, index) => {
    setProfile((prev) => ({
      ...prev,
      [field]: prev[field].filter((_, i) => i !== index)
    }))
  }

  if (loading) {
    return (
      <div className='min-h-screen bg-netflix-black flex items-center justify-center'>
        <div className='text-white text-xl'>Loading profile...</div>
      </div>
    )
  }

  return (
    <div className='min-h-screen bg-netflix-black text-white p-8'>
      {/* Header */}
      <div className='max-w-4xl mx-auto mb-8'>
        <button
          onClick={() => navigate('/')}
          className='text-netflix-red hover:text-netflix-darkRed mb-4 flex items-center'
        >
          <svg className='w-5 h-5 mr-2' fill='none' stroke='currentColor' viewBox='0 0 24 24'>
            <path strokeLinecap='round' strokeLinejoin='round' strokeWidth={2} d='M10 19l-7-7m0 0l7-7m-7 7h18' />
          </svg>
          Back to Chat
        </button>

        <h1 className='text-4xl font-bold mb-2'>Profile Settings</h1>
        <p className='text-gray-400'>Customize your preferences for personalized movie recommendations</p>
      </div>

      {/* Messages */}
      {message && <div className='max-w-4xl mx-auto mb-6 bg-green-600 text-white px-6 py-4 rounded-lg'>{message}</div>}
      {error && <div className='max-w-4xl mx-auto mb-6 bg-netflix-red text-white px-6 py-4 rounded-lg'>{error}</div>}

      {/* Settings Form */}
      <div className='max-w-4xl mx-auto space-y-8'>
        {/* User Info */}
        <div className='bg-netflix-darkGray p-6 rounded-lg'>
          <h2 className='text-2xl font-semibold mb-4'>User Information</h2>
          <div className='space-y-2'>
            <p>
              <span className='text-gray-400'>Name:</span> <span className='ml-2'>{userInfo.name}</span>
            </p>
            <p>
              <span className='text-gray-400'>Email:</span> <span className='ml-2'>{userInfo.email}</span>
            </p>
          </div>
        </div>

        {/* Preferences */}
        <div className='bg-netflix-darkGray p-6 rounded-lg'>
          <h2 className='text-2xl font-semibold mb-4'>General Preferences</h2>
          <textarea
            value={profile.preferences}
            onChange={(e) => setProfile({ ...profile, preferences: e.target.value })}
            placeholder='Describe what you love in movies... (e.g., "Love action-packed movies with intense fight scenes and plot twists")'
            className='w-full bg-netflix-black text-white border border-gray-600 rounded-lg p-4 h-32 focus:outline-none focus:border-netflix-red'
          />
        </div>

        {/* Favorite Genres */}
        <div className='bg-netflix-darkGray p-6 rounded-lg'>
          <h2 className='text-2xl font-semibold mb-4'>Favorite Genres</h2>
          <p className='text-gray-400 mb-4 text-sm'>Select genres you love</p>
          <div className='flex flex-wrap gap-2'>
            {genreOptions.map((genre) => (
              <button
                key={genre}
                onClick={() => toggleGenre(genre, 'favorite')}
                className={`px-4 py-2 rounded-full transition ${
                  profile.favorite_genres.includes(genre)
                    ? 'bg-netflix-red text-white'
                    : 'bg-netflix-black text-gray-400 hover:bg-gray-700'
                }`}
              >
                {genre}
              </button>
            ))}
          </div>
        </div>

        {/* Disliked Genres */}
        <div className='bg-netflix-darkGray p-6 rounded-lg'>
          <h2 className='text-2xl font-semibold mb-4'>Disliked Genres</h2>
          <p className='text-gray-400 mb-4 text-sm'>Select genres to avoid</p>
          <div className='flex flex-wrap gap-2'>
            {genreOptions.map((genre) => (
              <button
                key={genre}
                onClick={() => toggleGenre(genre, 'disliked')}
                className={`px-4 py-2 rounded-full transition ${
                  profile.disliked_genres.includes(genre)
                    ? 'bg-gray-700 text-white line-through'
                    : 'bg-netflix-black text-gray-400 hover:bg-gray-700'
                }`}
              >
                {genre}
              </button>
            ))}
          </div>
        </div>

        {/* Favorite Actors */}
        <div className='bg-netflix-darkGray p-6 rounded-lg'>
          <h2 className='text-2xl font-semibold mb-4'>Favorite Actors/Actresses</h2>
          <input
            type='text'
            value={actorSearch}
            onChange={(e) => setActorSearch(e.target.value)}
            onFocus={() => setShowActorDropdown(true)}
            placeholder='Search actors... (e.g., "Tom Cruise", "Leonardo DiCaprio")'
            className='w-full bg-netflix-black text-white border border-gray-600 rounded-lg p-3 focus:outline-none focus:border-netflix-red'
          />

          {/* Selected actors display */}
          {profile.favorite_actors.length > 0 && (
            <div className='mt-4'>
              <p className='text-sm text-gray-400 mb-2'>Selected ({profile.favorite_actors.length}):</p>
              <div className='flex flex-wrap gap-2'>
                {profile.favorite_actors.map((actor) => (
                  <span
                    key={actor}
                    className='bg-netflix-red text-white px-3 py-1 rounded-full text-sm flex items-center gap-2'
                  >
                    {actor}
                    <button onClick={() => toggleActor(actor)} className='hover:text-gray-300'>
                      ×
                    </button>
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Actor grid with search */}
          {(showActorDropdown || actorSearch) && (
            <div className='relative mt-4'>
              <div className='max-h-96 overflow-y-auto bg-netflix-black border border-gray-600 rounded-lg p-4'>
                <div className='grid grid-cols-2 md:grid-cols-3 gap-2'>
                  {filteredActors.map((actor) => (
                    <button
                      key={actor}
                      onClick={() => toggleActor(actor)}
                      className={`px-3 py-2 rounded text-sm transition text-left ${
                        isActorSelected(actor)
                          ? 'bg-netflix-red text-white'
                          : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                      }`}
                    >
                      {actor}
                    </button>
                  ))}
                </div>
                {filteredActors.length === 0 && <p className='text-gray-400 text-center py-4'>No actors found</p>}
              </div>
              <button
                onClick={() => {
                  setShowActorDropdown(false)
                  setActorSearch('')
                }}
                className='mt-2 w-full text-center text-sm text-gray-400 hover:text-white'
              >
                Close
              </button>
            </div>
          )}

          {!showActorDropdown && !actorSearch && (
            <button
              onClick={() => setShowActorDropdown(true)}
              className='mt-4 w-full bg-netflix-black hover:bg-gray-700 text-white border border-gray-600 rounded-lg p-3 transition'
            >
              {profile.favorite_actors.length > 0 ? 'Add More Actors' : 'Select Actors'}
            </button>
          )}
        </div>

        {/* Watch Style */}
        <div className='bg-netflix-darkGray p-6 rounded-lg'>
          <h2 className='text-2xl font-semibold mb-4'>Watch Style</h2>
          <input
            type='text'
            value={profile.watch_style}
            onChange={(e) => setProfile({ ...profile, watch_style: e.target.value })}
            placeholder='e.g., "Enjoys intense action sequences and complex storylines"'
            className='w-full bg-netflix-black text-white border border-gray-600 rounded-lg p-3 focus:outline-none focus:border-netflix-red'
          />
        </div>

        {/* Mood Preference */}
        <div className='bg-netflix-darkGray p-6 rounded-lg'>
          <h2 className='text-2xl font-semibold mb-4'>Current Mood</h2>
          <p className='text-gray-400 mb-4 text-sm'>What type of content are you in the mood for?</p>
          <div className='grid grid-cols-2 md:grid-cols-3 gap-3'>
            {moodOptions.map((mood) => (
              <button
                key={mood.value}
                onClick={() => setProfile({ ...profile, mood_preference: mood.label })}
                className={`px-4 py-3 rounded-lg transition text-left flex items-center gap-2 ${
                  profile.mood_preference === mood.label
                    ? 'bg-netflix-red text-white ring-2 ring-netflix-red ring-offset-2 ring-offset-netflix-darkGray'
                    : 'bg-netflix-black text-gray-300 hover:bg-gray-700'
                }`}
              >
                <span className='text-2xl'>{mood.emoji}</span>
                <span className='text-sm font-medium'>{mood.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Watching Context */}
        <div className='bg-netflix-darkGray p-6 rounded-lg'>
          <h2 className='text-2xl font-semibold mb-4'>Watching Context</h2>
          <div className='grid grid-cols-1 md:grid-cols-2 gap-4'>
            <div>
              <label className='block text-sm text-gray-400 mb-2'>Watching with</label>
              <select
                value={profile.watching_with}
                onChange={(e) => setProfile({ ...profile, watching_with: e.target.value })}
                className='w-full bg-netflix-black text-white border border-gray-600 rounded-lg p-3 focus:outline-none focus:border-netflix-red'
              >
                <option value='solo'>Solo</option>
                <option value='partner'>Partner</option>
                <option value='family'>Family</option>
                <option value='friends'>Friends</option>
              </select>
            </div>
            <div>
              <label className='block text-sm text-gray-400 mb-2'>Time available</label>
              <select
                value={profile.time_available}
                onChange={(e) => setProfile({ ...profile, time_available: e.target.value })}
                className='w-full bg-netflix-black text-white border border-gray-600 rounded-lg p-3 focus:outline-none focus:border-netflix-red'
              >
                <option value='< 1 hour'>Less than 1 hour</option>
                <option value='1-1.5 hours'>1-1.5 hours</option>
                <option value='1.5-2 hours'>1.5-2 hours</option>
                <option value='2-3 hours'>2-3 hours</option>
                <option value='> 3 hours'>More than 3 hours</option>
              </select>
            </div>
          </div>
        </div>

        {/* Language Preference */}
        <div className='bg-netflix-darkGray p-6 rounded-lg'>
          <h2 className='text-2xl font-semibold mb-4'>Country/Language Preference</h2>
          <p className='text-gray-400 mb-4 text-sm'>
            Select countries/regions for content recommendations (click to toggle)
          </p>

          {/* Search box */}
          <div className='mb-4'>
            <input
              type='text'
              value={languageSearch}
              onChange={(e) => setLanguageSearch(e.target.value)}
              onFocus={() => setShowLanguageDropdown(true)}
              placeholder='Search countries... (e.g., "Japan", "United States")'
              className='w-full bg-netflix-black text-white border border-gray-600 rounded-lg p-3 focus:outline-none focus:border-netflix-red'
            />
          </div>

          {/* Selected countries display */}
          {profile.language_preference && (
            <div className='mb-4'>
              <p className='text-sm text-gray-400 mb-2'>Selected:</p>
              <div className='flex flex-wrap gap-2'>
                {profile.language_preference.split(',').map((country) => {
                  const trimmed = country.trim()
                  if (!trimmed) return null
                  return (
                    <span
                      key={trimmed}
                      className='bg-netflix-red text-white px-3 py-1 rounded-full text-sm flex items-center gap-2'
                    >
                      {trimmed}
                      <button onClick={() => toggleCountry(trimmed)} className='hover:text-gray-300'>
                        ×
                      </button>
                    </span>
                  )
                })}
              </div>
            </div>
          )}

          {/* Country grid with search */}
          {(showLanguageDropdown || languageSearch) && (
            <div className='relative'>
              <div className='max-h-96 overflow-y-auto bg-netflix-black border border-gray-600 rounded-lg p-4'>
                <div className='grid grid-cols-2 md:grid-cols-3 gap-2'>
                  {filteredCountries.map((country) => (
                    <button
                      key={country}
                      onClick={() => toggleCountry(country)}
                      className={`px-3 py-2 rounded text-sm transition text-left ${
                        isCountrySelected(country)
                          ? 'bg-netflix-red text-white'
                          : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                      }`}
                    >
                      {country}
                    </button>
                  ))}
                </div>
                {filteredCountries.length === 0 && <p className='text-gray-400 text-center py-4'>No countries found</p>}
              </div>
              <button
                onClick={() => {
                  setShowLanguageDropdown(false)
                  setLanguageSearch('')
                }}
                className='mt-2 w-full text-center text-sm text-gray-400 hover:text-white'
              >
                Close
              </button>
            </div>
          )}

          {!showLanguageDropdown && !languageSearch && (
            <button
              onClick={() => setShowLanguageDropdown(true)}
              className='w-full bg-netflix-black hover:bg-gray-700 text-white border border-gray-600 rounded-lg p-3 transition'
            >
              {profile.language_preference ? 'Modify Selection' : 'Select Countries'}
            </button>
          )}
        </div>

        {/* Recently Watched */}
        <div className='bg-netflix-darkGray p-6 rounded-lg'>
          <h2 className='text-2xl font-semibold mb-4'>Recently Watched</h2>
          <div className='space-y-2'>
            {profile.recently_watched.map((title, index) => (
              <div key={index} className='flex items-center justify-between bg-netflix-black p-3 rounded'>
                <span>{title}</span>
                <button
                  onClick={() => removeFromList('recently_watched', index)}
                  className='text-netflix-red hover:text-netflix-darkRed'
                >
                  Remove
                </button>
              </div>
            ))}
            <input
              type='text'
              placeholder='Add movie/show title and press Enter'
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  addToList('recently_watched', e.target.value)
                  e.target.value = ''
                }
              }}
              className='w-full bg-netflix-black text-white border border-gray-600 rounded-lg p-3 focus:outline-none focus:border-netflix-red'
            />
          </div>
        </div>

        {/* Save Button */}
        <div className='flex justify-end gap-4'>
          <button
            onClick={() => navigate('/')}
            className='bg-gray-600 hover:bg-gray-700 text-white font-semibold px-8 py-3 rounded-lg transition'
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={saving}
            className='bg-netflix-red hover:bg-netflix-darkRed text-white font-semibold px-8 py-3 rounded-lg transition disabled:opacity-50'
          >
            {saving ? 'Saving...' : 'Save Profile'}
          </button>
        </div>
      </div>
    </div>
  )
}
