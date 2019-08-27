<?php
/**
 * The base configuration for WordPress
 *
 * The wp-config.php creation script uses this file during the
 * installation. You don't have to use the web site, you can
 * copy this file to "wp-config.php" and fill in the values.
 *
 * This file contains the following configurations:
 *
 * * MySQL settings
 * * Secret keys
 * * Database table prefix
 * * ABSPATH
 *
 * @link https://codex.wordpress.org/Editing_wp-config.php
 *
 * @package WordPress
 */

// ** MySQL settings - You can get this info from your web host ** //
/** The name of the database for WordPress */
define( 'DB_NAME', 'wordpress' );

/** MySQL database username */
define( 'DB_USER', 'root' );

/** MySQL database password */
define( 'DB_PASSWORD', '' );

/** MySQL hostname */
define( 'DB_HOST', 'localhost' );

/** Database Charset to use in creating database tables. */
define( 'DB_CHARSET', 'utf8mb4' );

/** The Database Collate type. Don't change this if in doubt. */
define( 'DB_COLLATE', '' );

/**#@+
 * Authentication Unique Keys and Salts.
 *
 * Change these to different unique phrases!
 * You can generate these using the {@link https://api.wordpress.org/secret-key/1.1/salt/ WordPress.org secret-key service}
 * You can change these at any point in time to invalidate all existing cookies. This will force all users to have to log in again.
 *
 * @since 2.6.0
 */
define( 'AUTH_KEY',         'pboSnZ:52~dki!%1rEQbc:8|ui)nd![:@Ff4{fMDnZcttz1;7q4[Cru*i Po}eO}' );
define( 'SECURE_AUTH_KEY',  'f.yk/j2z2+~F#fU5ny^$h-h;Y*9;st-j-YV$B;%==>NeF#WA5a. nHOV2^b#oXJs' );
define( 'LOGGED_IN_KEY',    'jywn:zPvjPKom)9UB>~kEO><ujO+zht).BD<}nn=hw)s:n Cn9P43#O_^jc/YusO' );
define( 'NONCE_KEY',        'J58~t&DK=Mg`as+u+@FxJ-f?Q/* V0F~D|iZmaZYp?i,hrB+7` q&@,t]MT[U3n3' );
define( 'AUTH_SALT',        '@]()LF-wqFDUK1|*aEP2IRxKcVDNXApj)D&U3FGN$R SB!!)<5)!DJLGOQiSM[B4' );
define( 'SECURE_AUTH_SALT', 'so?aGbalhq]UM!a# )&lUeOh{f:kFLgx9Z7--{YWpdc_q`g~?W.eND.:EUHvaW6#' );
define( 'LOGGED_IN_SALT',   'X2Nl?h&]!MBlN~YjplV8^i@JhX5Usn 5ml=1f. aeIU8<H6NW|xkm<e]{Ypf<;cc' );
define( 'NONCE_SALT',       'J@a1;h2-!bkQQ$}X)5Vegi-Y1k^K*jT1*$$L-gHPAw:D3~K*>Q>z+Nf*,ub!Pto9' );

/**#@-*/

/**
 * WordPress Database Table prefix.
 *
 * You can have multiple installations in one database if you give each
 * a unique prefix. Only numbers, letters, and underscores please!
 */
$table_prefix = 'wp_';

/**
 * For developers: WordPress debugging mode.
 *
 * Change this to true to enable the display of notices during development.
 * It is strongly recommended that plugin and theme developers use WP_DEBUG
 * in their development environments.
 *
 * For information on other constants that can be used for debugging,
 * visit the Codex.
 *
 * @link https://codex.wordpress.org/Debugging_in_WordPress
 */
define( 'WP_DEBUG', false );

/* That's all, stop editing! Happy publishing. */

/** Absolute path to the WordPress directory. */
if ( ! defined( 'ABSPATH' ) ) {
        define( 'ABSPATH', dirname( __FILE__ ) . '/' );
}

/** Sets up WordPress vars and included files. */
require_once( ABSPATH . 'wp-settings.php' );