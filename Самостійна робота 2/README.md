# СР №2: Система управління базою даних книг бібліотеки

Python 3.9+, лише стандартна бібліотека (додаткових залежностей немає).

## Запуск
    python main.py demo       # демонстрація: метакласи, валідація, пошук, видача, JSON
    python main.py threads    # мультипотокові сценарії та заміри продуктивності
    python main.py            # обидва режими
    python -m unittest discover -s tests -v   # 27 юніт-тестів

Журнал роботи записується у logs/library.log, дані — у data/library.json.

## Структура
    main.py                      точка входу
    demo_data.py                 початкові дані
    library_system/
        exceptions.py            ієрархія виключень
        metaclasses.py           LoggingMeta, SingletonMeta
        validators.py            перевірки (рядок, діапазон, e-mail, ISBN-13, тип)
        decorators.py            validate_args, log_call, synchronized
        models.py                Author, Book, Reader
        repository.py            Repository
        factory.py               EntityFactory
        events.py                EventBus, Observer, AuditObserver, StatisticsObserver
        search.py                Strategy: ByTitle, ByAuthor, ByYearRange, AvailableOnly
        service.py               LibraryService (фасад, Singleton, потокобезпечний)
        concurrency.py           RequestProcessor (ThreadPoolExecutor)
        logging_config.py        налаштування логування
    tests/test_library.py        юніт-тести
