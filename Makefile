dev:
	@OTREE_ADMIN_PASSWORD=admin OTREE_AUTH_LEVEL=STUDY otree devserver :8180
prod:
	@DATABASE_URL=postgres://postgres:postgres@localhost:5432/postgres OTREE_PRODUCTION=1 OTREE_ADMIN_PASSWORD=admin OTREE_AUTH_LEVEL=STUDY otree prodserver :8180
buildfront:
	@node ./_front/process/clear-static.mjs && node ./_front/process/esbuild.mjs && node ./_front/process/update-templates.mjs
dockerbuild:
	@docker build -f _docker/Dockerfile.build -t experiment:latest . && docker tag experiment ducksouplab/experiment
dockerpush:
	@docker push ducksouplab/experiment:latest
dockerexec:
	@docker run -t -i --rm experiment:latest sh
