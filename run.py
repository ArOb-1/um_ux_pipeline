import argparse
import uvicorn


def main():
    parser = argparse.ArgumentParser(description="Запуск UMUX Pipeline API")
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Хост для запуска (по умолчанию: 127.0.0.1)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Порт для запуска (по умолчанию: 8000)"
    )
    parser.add_argument(
        "--no-reload",
        action="store_true",
        help="Отключить auto-reload"
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("🚀 ЗАПУСК UMUX PIPELINE API")
    print("="*60)
    print(f"📡 Сервер: http://{args.host}:{args.port}")
    print(f"📚 Документация: http://{args.host}:{args.port}/docs")
    print("="*60 + "\n")
    
    uvicorn.run(
        "app.main:app",
        host=args.host,
        port=args.port,
        reload=not args.no_reload,
        log_level="info"
    )


if __name__ == "__main__":
    main()
