from app.services.ingest import ingest
from app.core.rag import ask
from app.services.evaluation import evaluate


def main():
    while True:
        print("\n" + "=" * 40)
        print("  AI Bilgi Asistanı")
        print("=" * 40)
        print("1 -> Döküman yükle")
        print("2 -> Soru sor")
        print("3 -> Değerlendirme çalıştır")
        print("4 -> Çıkış")

        choice = input("\nSeçiminiz: ").strip()

        if choice == "1":
            ingest()
        elif choice == "2":
            question = input("Sorunuzu yazın: ")
            answer, sources = ask(question)
            print("\nCevap:\n", answer)
            print("\nKaynaklar:\n", sources)
        elif choice == "3":
            print("\nDeğerlendirme çalıştırılıyor...")
            results = evaluate()
            for result in results:
                print(result)
        elif choice == "4":
            print("Çıkış yapılıyor...")
            break
        else:
            print("Geçersiz seçim, tekrar deneyin.")


if __name__ == "__main__":
    main()