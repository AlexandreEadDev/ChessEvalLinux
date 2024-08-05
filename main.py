import os
import random

import chess
import chess.engine
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins


@app.route("/evaluate", methods=["POST"])
def evaluate():
    try:
        # Extract FEN and level from the request
        data = request.json
        fen = data.get("fen")
        level = data.get("level", 1)

        if not fen:
            return jsonify({"error": "FEN is required"}), 400

        board = chess.Board(fen)

        # Path to Stockfish executable
        stockfish_path = os.path.join(
            os.path.dirname(__file__), "stockfish-ubuntu-x86-64-avx2"
        )

        with chess.engine.SimpleEngine.popen_uci(stockfish_path) as engine:
            # Analyze the position with Stockfish
            result = engine.analyse(board, chess.engine.Limit(time=0.1), multipv=5)

            # Extract moves and their scores
            moves_scores = [
                (entry["pv"][0].uci(), entry["score"].white().score(mate_score=10000))
                for entry in result
            ]

            if level == 1:
                chosen_move = random.choice(moves_scores[:5])[
                    0
                ]  # Chooses randomly from the top 5 moves
            elif level == 2:
                chosen_move = random.choice(moves_scores[:3])[
                    0
                ]  # Chooses randomly from the top 3 moves
            else:  # level == 3 or any other value
                chosen_move = moves_scores[0][0]  # Always chooses the best move

            evaluation = moves_scores[0][1]  # Evaluation of the best move

        return jsonify(
            {
                "evaluation": evaluation,
                "move_to_play": chosen_move,
                "best_move": moves_scores[0][0],
            }
        )

    except KeyError as e:
        return jsonify({"error": f"Missing key in request data: {e}"}), 400

    except chess.engine.EngineTerminatedError:
        return jsonify({"error": "Chess engine terminated unexpectedly"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port, debug=True)
