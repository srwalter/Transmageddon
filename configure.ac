AC_PREREQ(2.52)

dnl initialize autoconf
dnl when going to/from release please set the nano (fourth number) right !
dnl releases only do Wall, cvs and prerelease does Werror too
AC_INIT(transmageddon, 0.9,
    http://www.linuxrising.org/transmageddon,
    transmageddon)

dnl initialize automake
AM_INIT_AUTOMAKE

dnl define PACKAGE_VERSION_* variables
AS_VERSION

dnl can autoconf find the source ?
AC_CONFIG_SRCDIR([src/transmageddon.py])


AC_SUBST_FILE(AUTHORS)
AUTHORS=$srcdir/AUTHORS

dnl Note for packagers
dnl The following requirements are run-time requirements,
dnl make sure you don't forget them, even though you're able to
dnl build pitivi without them.
dnl
dnl For a more exhaustive list of checks, you can have a look at
dnl the runtime checks in pitivi/check.py

AC_SUBST(PYGTK_REQ, 2.8.0)
AC_SUBST(PYGST_REQ, 0.10.6)
AC_SUBST(GST_REQ, 0.10.13.1)

AM_INIT_AUTOMAKE($PACKAGE, $VERSION)
AC_SUBST(ACLOCAL_AMFLAGS, "-I common/m4")

AS_AC_EXPAND(LIBDIR, $libdir)
AC_MSG_NOTICE(Storing library files in $LIBDIR)

AS_AC_EXPAND(DATADIR, $datadir)
AC_MSG_NOTICE(Storing data files in $DATADIR)

AS_AC_EXPAND(SYSCONFDIR, $sysconfdir)
AC_MSG_NOTICE(Storing configuration files in $SYSCONFDIR)

AS_AC_EXPAND(LOCALSTATEDIR, $localstatedir)
AC_MSG_NOTICE(Using localstatedir $LOCALSTATEDIR)

dnl check for python
AS_PATH_PYTHON(2.5)

dnl enable i18n
ALL_LINGUAS="pl"
GETTEXT_PACKAGE="transmageddon"
AC_SUBST([GETTEXT_PACKAGE])
AC_DEFINE_UNQUOTED([GETTEXT_PACKAGE], "$GETTEXT_PACKAGE", [Gettext package])
AM_GLIB_GNU_GETTEXT
IT_PROG_INTLTOOL([0.35.0])

CONFIGURED_PYTHONPATH=$PYTHONPATH
AC_SUBST(CONFIGURED_PYTHONPATH)

AC_CONFIG_FILES([bin/transmageddon], [chmod +x bin/transmageddon])

dnl output stuff
AC_OUTPUT(
Makefile
bin/Makefile
common/Makefile
common/m4/Makefile
src/Makefile
debian/Makefile
po/Makefile.in
transmageddon.spec
transmageddon.desktop.in
)
