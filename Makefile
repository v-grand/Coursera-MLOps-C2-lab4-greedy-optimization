install:
	pip install --upgrade pip &&\
		pip install -r requirements.txt

test:
	python -m pytest -vv --cov=main --cov=mylib --cov=tsp --cov=greedy_coin test_*.py

format:	
	black *.py 

lint:
	pylint --disable=R,C --ignore-patterns=test_.*?py *.py mylib/*.py

demo-greedy:
	@echo "Demo: Greedy Coin Change"
	python greedy_coin.py --dollars 1 --cents 50
	python greedy_coin.py --cents 99

demo-tsp:
	@echo "Demo: TSP with auto-stop"
	python tsp.py simulate --count 30 --auto-stop

demo: demo-greedy demo-tsp

container-lint:
	docker run --rm -i hadolint/hadolint < Dockerfile

refactor: format lint

deploy:
	#deploy goes here
		
all: install lint test format deploy
