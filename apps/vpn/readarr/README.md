# Readarr (Audio)

## Status: DISABLED

This component is **disabled** (`suspend: true` in `ks.yaml`): the [Readarr project was retired upstream on 2025-06-27](https://github.com/Readarr/Readarr).
The upstream repository is archived: there will be no further releases, bugfixes or security patches. The running
instance (image `ghcr.io/home-operations/readarr:0.4.18`) keeps working but will never be updated.

## Replacement

This instance was used for audiobooks. Consider:

- [Audiobookshelf](https://www.audiobookshelf.org/) - self-hosted audiobook & podcast server with playback and mobile apps (recommended for the audiobook use case)
- [LazyLibrarian](https://gitlab.com/LazyLibrarian/LazyLibrarian) - the *arr-style automated searcher for books/audiobooks that is still actively developed
- [Calibre-Web](https://github.com/janeczku/calibre-web) - ebook library management

## How to re-enable

Remove the `suspend: true` line in [ks.yaml](ks.yaml) and let Flux reconcile.
