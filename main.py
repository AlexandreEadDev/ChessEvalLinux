from flask import Flask, request, jsonify
from flask_cors import CORS
import chess
import chess.engine
import random
import os
import ssl

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/evaluate', methods=['POST'])
def evaluate():
    fen = request.json['fen']
    level = request.json['level']
    board = chess.Board(fen)

    with chess.engine.SimpleEngine.popen_uci("stockfish-ubuntu-x86-64-avx2") as engine:
        result = engine.analyse(board, chess.engine.Limit(time=0.1), multipv=5)
        moves_scores = [(entry['pv'][0].uci(), entry['score'].white().score(mate_score=10000)) for entry in result]

        if level == 1:
            chosen_move = random.choice(moves_scores[:5])[0]  # Chooses randomly from the top 5 moves
        elif level == 2:
            chosen_move = random.choice(moves_scores[:3])[0]  # Chooses randomly from the top 3 moves
        else:  # level == 3 or any other value
            chosen_move = moves_scores[0][0]  # Always chooses the best move

        evaluation = moves_scores[0][1]  # Evaluation of the best move

    return jsonify({'evaluation': evaluation, 'move_to_play': chosen_move, 'best_move':  moves_scores[0][0]})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))

    # Path to SSL certificate and key files
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain('/etc/letsencrypt/live/evaluatechesspositionfromfen.xyz/fullchain.pem', '/etc/letsencrypt/live/evaluatechesspositionfromfen.xyz/privkey.pem')

    # Run the app with SSL context
    app.run(host='0.0.0.0', port=port, debug=True, ssl_context=ssl_context)
