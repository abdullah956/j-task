import ChatWidget from './components/ChatWidget';

function App() {
  return (
    <div style={styles.container}>
      <ChatWidget />
    </div>
  );
}

const styles = {
  container: {
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    background: 'linear-gradient(135deg, #0d9488 0%, #14b8a6 50%, #5eead4 100%)',
    padding: '20px',
  },
};

export default App;
