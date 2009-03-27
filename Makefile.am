AUTOMAKE_OPTIONS = dist-bzip2

SUBDIRS	= bin src common

desktopdir = $(datadir)/applications
desktop_DATA = transmageddon.desktop

icondir = $(datadir)/pixmaps
icon_DATA = transmageddon.png

transmageddondir = $(libdir)/transmageddon
transmageddon_DATA = transmageddon.png

EXTRA_DIST = \
	transmageddon.spec \
	transmageddon.spec.in \
	ChangeLog \
	autogen.sh \
	NEWS \
	AUTHORS \
	RELEASE \
	ABOUT-NLS \
	transmageddon.png \
	$(INTLTOOL)


DISTCLEANFILES =                \
        intltool-extract        \
        intltool-merge          \
        intltool-update		\
	autoregen.sh		\
	config.log		\
	Makefile		\
	Makefile.in		\
	missing			\
	mkinstalldirs		\
	py-compile		\
	config.status		\
	install-sh		\
	configure


EXTRA_DIST +=                    \
        intltool-extract.in     \
        intltool-merge.in       \
        intltool-update.in	\
	TODO

locale-uninstalled:
	if test -d po; then \
	    $(MAKE) -C po datadir=../$(top_builddir) install; \
	fi

locale-uninstalled-clean:
	@-rm -rf _trial_temp
	@-rm -rf $(top_builddir)/locale


all-local: locale-uninstalled
clean-local: locale-uninstalled-clean
