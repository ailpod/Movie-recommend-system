"""添加评分表

Revision ID: add_ratings_table
Revises: 
Create Date: 2025-12-23

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func


# revision identifiers, used by Alembic.
revision = 'add_ratings_table'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 创建评分表
    op.create_table(
        'ratings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('movie_id', sa.Integer(), nullable=False),
        sa.Column('rating', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=func.now(), onupdate=func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['movie_id'], ['movies.id'], )
    )
    
    # 创建索引
    op.create_index('ix_ratings_user_id', 'ratings', ['user_id'])
    op.create_index('ix_ratings_movie_id', 'ratings', ['movie_id'])
    
    # 为用户ID和电影ID组合创建唯一约束，确保一个用户对一部电影只能有一个评分
    op.create_index('ix_ratings_user_movie', 'ratings', ['user_id', 'movie_id'], unique=True)


def downgrade() -> None:
    # 删除索引
    op.drop_index('ix_ratings_user_movie', table_name='ratings')
    op.drop_index('ix_ratings_movie_id', table_name='ratings')
    op.drop_index('ix_ratings_user_id', table_name='ratings')
    
    # 删除表
    op.drop_table('ratings')
