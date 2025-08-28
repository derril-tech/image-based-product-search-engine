-- Row Level Security (RLS) Policies for Image Search Application

-- Organizations policies
CREATE POLICY "Users can view their own organizations" ON organizations
    FOR SELECT USING (
        id IN (
            SELECT organization_id 
            FROM organization_memberships 
            WHERE user_id = current_setting('app.current_user_id')::uuid
        )
    );

CREATE POLICY "Organization owners can update their organizations" ON organizations
    FOR UPDATE USING (
        id IN (
            SELECT organization_id 
            FROM organization_memberships 
            WHERE user_id = current_setting('app.current_user_id')::uuid
            AND role = 'owner'
        )
    );

-- Users policies
CREATE POLICY "Users can view their own profile" ON users
    FOR SELECT USING (id = current_setting('app.current_user_id')::uuid);

CREATE POLICY "Users can update their own profile" ON users
    FOR UPDATE USING (id = current_setting('app.current_user_id')::uuid);

CREATE POLICY "Organization admins can view organization members" ON users
    FOR SELECT USING (
        id IN (
            SELECT user_id 
            FROM organization_memberships 
            WHERE organization_id = current_setting('app.current_organization_id')::uuid
            AND EXISTS (
                SELECT 1 FROM organization_memberships 
                WHERE user_id = current_setting('app.current_user_id')::uuid
                AND organization_id = current_setting('app.current_organization_id')::uuid
                AND role IN ('owner', 'admin')
            )
        )
    );

-- Organization memberships policies
CREATE POLICY "Users can view their own memberships" ON organization_memberships
    FOR SELECT USING (user_id = current_setting('app.current_user_id')::uuid);

CREATE POLICY "Organization admins can view all memberships" ON organization_memberships
    FOR SELECT USING (
        organization_id = current_setting('app.current_organization_id')::uuid
        AND EXISTS (
            SELECT 1 FROM organization_memberships 
            WHERE user_id = current_setting('app.current_user_id')::uuid
            AND organization_id = current_setting('app.current_organization_id')::uuid
            AND role IN ('owner', 'admin')
        )
    );

CREATE POLICY "Organization owners can manage memberships" ON organization_memberships
    FOR ALL USING (
        organization_id = current_setting('app.current_organization_id')::uuid
        AND EXISTS (
            SELECT 1 FROM organization_memberships 
            WHERE user_id = current_setting('app.current_user_id')::uuid
            AND organization_id = current_setting('app.current_organization_id')::uuid
            AND role = 'owner'
        )
    );

-- Products policies
CREATE POLICY "Users can view products in their organization" ON products
    FOR SELECT USING (
        organization_id = current_setting('app.current_organization_id')::uuid
    );

CREATE POLICY "Users can create products in their organization" ON products
    FOR INSERT WITH CHECK (
        organization_id = current_setting('app.current_organization_id')::uuid
    );

CREATE POLICY "Users can update products in their organization" ON products
    FOR UPDATE USING (
        organization_id = current_setting('app.current_organization_id')::uuid
    );

CREATE POLICY "Users can delete products in their organization" ON products
    FOR DELETE USING (
        organization_id = current_setting('app.current_organization_id')::uuid
    );

-- Product variants policies
CREATE POLICY "Users can view variants in their organization" ON product_variants
    FOR SELECT USING (
        product_id IN (
            SELECT id FROM products 
            WHERE organization_id = current_setting('app.current_organization_id')::uuid
        )
    );

CREATE POLICY "Users can manage variants in their organization" ON product_variants
    FOR ALL USING (
        product_id IN (
            SELECT id FROM products 
            WHERE organization_id = current_setting('app.current_organization_id')::uuid
        )
    );

-- Images policies
CREATE POLICY "Users can view images in their organization" ON images
    FOR SELECT USING (
        organization_id = current_setting('app.current_organization_id')::uuid
    );

CREATE POLICY "Users can manage images in their organization" ON images
    FOR ALL USING (
        organization_id = current_setting('app.current_organization_id')::uuid
    );

-- Embeddings policies
CREATE POLICY "Users can view embeddings in their organization" ON embeddings
    FOR SELECT USING (
        organization_id = current_setting('app.current_organization_id')::uuid
    );

CREATE POLICY "Users can manage embeddings in their organization" ON embeddings
    FOR ALL USING (
        organization_id = current_setting('app.current_organization_id')::uuid
    );

-- Regions policies
CREATE POLICY "Users can view regions in their organization" ON regions
    FOR SELECT USING (
        image_id IN (
            SELECT id FROM images 
            WHERE organization_id = current_setting('app.current_organization_id')::uuid
        )
    );

CREATE POLICY "Users can manage regions in their organization" ON regions
    FOR ALL USING (
        image_id IN (
            SELECT id FROM images 
            WHERE organization_id = current_setting('app.current_organization_id')::uuid
        )
    );

-- Search sessions policies
CREATE POLICY "Users can view their own search sessions" ON search_sessions
    FOR SELECT USING (
        user_id = current_setting('app.current_user_id')::uuid
        OR organization_id = current_setting('app.current_organization_id')::uuid
    );

CREATE POLICY "Users can create search sessions in their organization" ON search_sessions
    FOR INSERT WITH CHECK (
        organization_id = current_setting('app.current_organization_id')::uuid
    );

-- Search feedback policies
CREATE POLICY "Users can view feedback in their organization" ON search_feedback
    FOR SELECT USING (
        session_id IN (
            SELECT id FROM search_sessions 
            WHERE organization_id = current_setting('app.current_organization_id')::uuid
        )
    );

CREATE POLICY "Users can create feedback in their organization" ON search_feedback
    FOR INSERT WITH CHECK (
        session_id IN (
            SELECT id FROM search_sessions 
            WHERE organization_id = current_setting('app.current_organization_id')::uuid
        )
    );

-- Connectors policies
CREATE POLICY "Users can view connectors in their organization" ON connectors
    FOR SELECT USING (
        organization_id = current_setting('app.current_organization_id')::uuid
    );

CREATE POLICY "Organization admins can manage connectors" ON connectors
    FOR ALL USING (
        organization_id = current_setting('app.current_organization_id')::uuid
        AND EXISTS (
            SELECT 1 FROM organization_memberships 
            WHERE user_id = current_setting('app.current_user_id')::uuid
            AND organization_id = current_setting('app.current_organization_id')::uuid
            AND role IN ('owner', 'admin')
        )
    );

-- Data feeds policies
CREATE POLICY "Users can view feeds in their organization" ON data_feeds
    FOR SELECT USING (
        organization_id = current_setting('app.current_organization_id')::uuid
    );

CREATE POLICY "Organization admins can manage feeds" ON data_feeds
    FOR ALL USING (
        organization_id = current_setting('app.current_organization_id')::uuid
        AND EXISTS (
            SELECT 1 FROM organization_memberships 
            WHERE user_id = current_setting('app.current_user_id')::uuid
            AND organization_id = current_setting('app.current_organization_id')::uuid
            AND role IN ('owner', 'admin')
        )
    );

-- Audit log policies
CREATE POLICY "Users can view audit logs in their organization" ON audit_log
    FOR SELECT USING (
        organization_id = current_setting('app.current_organization_id')::uuid
        AND EXISTS (
            SELECT 1 FROM organization_memberships 
            WHERE user_id = current_setting('app.current_user_id')::uuid
            AND organization_id = current_setting('app.current_organization_id')::uuid
            AND role IN ('owner', 'admin')
        )
    );

-- Function to set current user context
CREATE OR REPLACE FUNCTION set_user_context(user_id uuid, organization_id uuid)
RETURNS void AS $$
BEGIN
    PERFORM set_config('app.current_user_id', user_id::text, false);
    PERFORM set_config('app.current_organization_id', organization_id::text, false);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to clear user context
CREATE OR REPLACE FUNCTION clear_user_context()
RETURNS void AS $$
BEGIN
    PERFORM set_config('app.current_user_id', NULL, false);
    PERFORM set_config('app.current_organization_id', NULL, false);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
