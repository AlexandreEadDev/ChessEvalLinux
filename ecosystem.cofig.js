module.exports = {
  apps: [
    {
      name: "chess-evaluation-api",
      script: "main.py",
      interpreter: "python3",
      cwd: "/projects/ChessEvalLinux",
      env: {
        PORT: 5000,
        FLASK_ENV: "production",
      },
    },
  ],
};
