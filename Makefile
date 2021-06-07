test:
	@pre-commit run --all-files

run:
	@python3 -m uploadtgbot

clean:
	@pyclean .
	@rm -rf uploadtgbot/logs/ uploadtgbot/downloads/
