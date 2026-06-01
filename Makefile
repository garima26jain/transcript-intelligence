.PHONY: help install ingest enrich mcp demo spotcheck ui clean

help:
	@echo "Transcript Intelligence — make targets"
	@echo "  install     Install Python dependencies from requirements.txt"
	@echo "  ingest      Normalize raw transcripts → data/processed/transcripts.jsonl"
	@echo "  enrich      Run LLM enrichment → data/enriched/*.json"
	@echo "  mcp         Start the custom MCP server (stdio)"
	@echo "  demo        Run the LangGraph coordinator over example queries"
	@echo "  spotcheck   Produce the 10–15 transcript methodology table"
	@echo "  ui          Launch the Streamlit CS-lead view"
	@echo "  clean       Remove enriched outputs (keeps raw data)"

install:
	pip install -r requirements.txt

ingest:
	python -m scripts.run_ingest

enrich:
	python -m scripts.run_enrich

build-db:
	python -m scripts.build_db

mcp: build-db
	python -m scripts.start_mcp

demo:
	python -m scripts.demo

spotcheck:
	python -m scripts.run_spotcheck

ui:
	PYTHONPATH=. streamlit run ti/ui/app.py

clean:
	rm -rf data/processed data/enriched data/graph
	mkdir -p data/processed data/enriched data/graph
